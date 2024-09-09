# Usage: python3 video_highlight.py --input path-to-video-file
import argparse
import os
import random
import string
import subprocess
import re
from pathlib import Path
import concurrent.futures


def run_command(command, get_output=False, check=True):
	"""Execute a command through subprocess.run and return its output if required."""
	try:
		print(f"Executing: {' '.join(command)}")
		process = subprocess.run(command, stdout=subprocess.PIPE,
		                         stderr=subprocess.PIPE, text=True,
		                         check=check)
		return process.stdout.strip() + '\n' + process.stderr.strip() if get_output else None
	except subprocess.CalledProcessError as e:
		print(f"Error executing command: {' '.join(command)}\n{e}")
		if check:
			raise
		return None


def get_video_duration(video_path):
	"""Uses FFprobe to get the duration of a video."""
	cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
	       'default=noprint_wrappers=1:nokey=1', str(video_path)]
	output = run_command(cmd, get_output=True)
	if output:
		try:
			duration = float(output.strip())
			return duration
		except ValueError as e:
			print(f"Failed to parse video duration: {e}")
	else:
		print("FFprobe did not return any output.")
	return 0.0


def get_volume_info(video_file):
	"""Extracts volume information using FFmpeg."""
	cmd = ['ffmpeg', '-i', str(video_file), '-vn', '-af',
	       'aresample=22050,volumedetect', '-f', 'null', '-']
	output = run_command(cmd, get_output=True)
	max_volume = re.search(r"max_volume: ([\-\d\.]+) dB", output)
	mean_volume = re.search(r"mean_volume: ([\-\d\.]+) dB", output)
	return max_volume.group(1) if max_volume else "N/A", mean_volume.group(
		1) if mean_volume else "N/A"


def sec_to_ts(seconds):
	hours = int(seconds // 3600)
	minutes = int((seconds % 3600) // 60)
	seconds = round(seconds % 60, 2)
	return f"{hours:02}:{minutes:02}:{seconds:02}"


def cut_segment(i, pair, seg_files, input_video):
	input_video_name = os.path.splitext(os.path.basename(input_video))[0]
	seg_file = f"/tmp/{input_video_name}_seg_{i:02x}.mp4"
	start_time, end_time = pair[0], pair[1]
	cmd = [
		"ffmpeg",
		"-y",
		"-hide_banner",
		"-loglevel", "quiet",
		"-copyts",
		"-ss", start_time,
		"-i", input_video,
		"-ss", str(start_time),
		"-to", str(end_time),
		# "-c", "copy",
		"-c:v", "libx264",
		"-c:a", "aac",
		seg_file
	]

	run_command(cmd)
	print(f"Segment {i}/{len(seg_files)} is saved as {seg_file}")
	seg_files[i] = seg_file


def processVideo(input_video, output_video):
	origin_duration = get_video_duration(input_video)
	if origin_duration <= 0:
		print("Invalid video duration.")
		return
	print(f"The duration of the original video is: {origin_duration} seconds")

	max_volume, mean_volume = get_volume_info(input_video)
	print(f"Max Volume = {max_volume} db, Mean Volume = {mean_volume} db")

	command = ['ffmpeg', '-i', str(input_video), '-vn', '-af',
	           f'aresample=22050,silencedetect=noise={float(max_volume)-20.0}dB:d=3', '-f', 'null',
	           '-']
	output = run_command(command, get_output=True)

	# Parse the silence segments and convert to floating format
	silence_starts = [float(match) + 1.0 for match in
	                  re.findall(r'silence_start: (\d+\.?\d*)', output)]
	silence_ends = [float(match) - 0.5 for match in
	                re.findall(r'silence_end: (\d+\.?\d*)', output)]

	if not silence_starts:
		print("No silent segments are found")
		return

	# Add the end time of the video as the last silence beginning
	silence_starts.append(origin_duration)
	# Add the beginning time of the video as the first non-silence end
	silence_ends.insert(0, 0.0)

	# Calculate all non-silence segments
	reserve_segs = list(zip(silence_ends, silence_starts))
	reserve_segs = [(start, end) for start, end in reserve_segs if
	                end - start >= 4.0]
	result_duration = sum(end - start for start, end in reserve_segs)
	reserve_segs = [(sec_to_ts(range[0]), sec_to_ts(range[1])) for range in
	                reserve_segs]
	print(
		f"Extracting [{len(reserve_segs)}] highlight segments, highlight/origin={result_duration:.2f}/{origin_duration:.2f} seconds: {reserve_segs}")

	seg_files = [''] * len(reserve_segs)
	# ThreadPoolExecutor
	with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
		results = [
			executor.submit(cut_segment, index, pair, seg_files, input_video)
			for index, pair
			in enumerate(reserve_segs)]
		concurrent.futures.wait(results)

	video_list = f"{Path('/tmp')}/video_list_{''.join(random.choices(string.ascii_letters + string.digits, k=10))}.txt"
	#print(f"video list file = {video_list}")

	with open(video_list, "w") as file_list:
		for seg_file in seg_files:
			file_list.write(f"file '{seg_file}'\n")

	concat_command = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'quiet',
	                  '-f', 'concat', '-safe', '0', '-i', str(video_list),
	                  '-c', 'copy',
	                  # '-c:v','libx264',
	                  # '-c:a', 'aac',
	                  str(output_video)]
	run_command(concat_command)
	print(
		f"Output highlight video to {output_video}, extract {result_duration:.2f} seconds from {origin_duration:.2f} seconds, rate={100.0 * result_duration / origin_duration:.2f} %")

	# Delete those segments
	for seg_file in seg_files:
		os.remove(seg_file)

	os.remove(video_list)


def main():
	# Parse arguments
	parser = argparse.ArgumentParser(
		description="Extract the highlights of the video")
	parser.add_argument("-i", "--input", help="path to the input video file")
	parser.add_argument("-o", "--output", default="",
	                    help="path to the output video file")
	args = parser.parse_args()

	# Process starts here
	input = args.input
	if input is None:
		parser.print_usage()
		return
	output = args.output or f"{os.path.splitext(input)[0]}_highlight.mp4"
	processVideo(input, output)


if __name__ == "__main__":
	main()
