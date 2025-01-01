from pytube import YouTube


def downloadVideo(video_url, output_path="."):
    try:
        yt = YouTube(video_url)
        video_stream = yt.streams.get_highest_resolution()

        video_stream.download(output_path)

        print("Download completed successfully!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def downloaAudioMP3(video_url, output_path=".", filename=None):
    try:
        yt = YouTube(video_url)

        # Get the highest resolution audio stream
        audio_stream = yt.streams.filter(only_audio=True).first()

        if filename == None:
            filename = yt.title

        ending = filename.split(".")[-1]

        if ending == ".mp4":
            filename = filename[:-4] + ".mp3"

        elif ending != ".mp3":
            filename += ".mp3"

        # Download the audio stream
        audio_stream.download(output_path, filename=filename)

        print(f"Downloaded {filename} successfully!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

