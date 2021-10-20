import pandas as pd
import json
from urllib.request import urlopen
import streamlit as st
from datetime import datetime
from hashlib import sha1
import sage_data_client


@st.cache(ttl=3600)
def get_nodes_last_30_days():
    df = sage_data_client.query(
        start="-30d",
        tail=1,
        filter={
            "name": "upload",
            "vsn": ".*",
        }
    )
    return sorted(set(df["meta.vsn"].dropna()))


st.sidebar.title("Upload Viewer")
node = st.sidebar.selectbox("Node", get_nodes_last_30_days())
date = st.sidebar.date_input("Date")
time = st.sidebar.time_input("Time")
window = pd.to_timedelta(st.sidebar.text_input("Time Window", "1h"))
media_type = st.sidebar.selectbox("Media Type", ["Image", "Audio"])
st.sidebar.text("Datetime is in UTC!")
st.sidebar.text("05:00 UTC = midnight CST")
st.sidebar.text("17:00 UTC = noon CST")

dt = datetime(date.year, date.month, date.day, time.hour, time.minute, time.second)
start = dt - window
end = dt + window

query = {
    "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "filter": {
        "name": "upload",
        "vsn": node,
    }
}

st.title("Results")
st.code(f"curl -s -H 'Content-Type: application/json' https://data.sagecontinuum.org/api/v1/query -d \'{json.dumps(query)}\'")

df = sage_data_client.query(**query)
if len(df) == 0:
    st.warning(f"No query results found!")
    st.stop()

if media_type == "Audio":
    audios = df[df.value.str.endswith(".flac") | df.value.str.endswith(".mp3") | df.value.str.endswith(".wav")]

    if len(audios) == 0:
        st.warning(f"No audio found!")
        st.stop()

    st.title("Audio Samples")

    urls = list(audios.value)
    stride = len(urls)//16 + 1
    if stride > 1:
        st.warning(f"Too many images ({len(urls)}). Showing every {stride} images.")
    for url in urls[::stride]:
        st.audio(url)
        st.caption(url)
elif media_type == "Image":
    images = df[df.value.str.endswith(".jpg") | df.value.str.endswith(".png")]

    if len(images) == 0:
        st.warning(f"No images found!")
        st.stop()

    # add download file and button
    download_file = "\n".join(images.value)
    download_file += "\n"
    filename = "urls-" + sha1(download_file.encode()).hexdigest()[:8] + ".txt"
    st.sidebar.download_button("Download Image List", download_file, filename)
    st.sidebar.code(f"# download all urls with wget\nwget -r -N -i {filename}")

    for plugin, df_plugin in images.groupby("meta.plugin"):
        st.title(plugin)

        urls = list(df_plugin.value)
        captions = list(df_plugin.timestamp)

        stride = len(urls)//16 + 1
        if stride > 1:
            st.warning(f"Too many images ({len(urls)}). Showing every {stride} images.")
        st.image(urls[::stride], caption=captions[::stride], width=640)
