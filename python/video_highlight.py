# Usage: python3 video_highlight.py --input path-to-video-file
import argparse
import multiprocessing
import os
import random
import re
import string
import subprocess
import time
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
	refine_name = re.sub(r'[ /\\]', '-', input_video_name) # replace special chars in the name
	seg_file = f"/tmp/{refine_name}_seg_{i:02x}.mp4"
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
		#"-c:v", "h264_videotoolbox",  #higher speed but larger file size, libx265 is slower
		"-c:v", "libx264",
		"-c:a", "aac",
		seg_file
	]

	run_command(cmd)
	print(f"Segment {i}/{len(seg_files)} is saved as {seg_file}")
	seg_files[i] = seg_file


def get_reserve_segs(audio_track, origin_duration):
	"""
	Calculate the segment list from given audio or video
	:param audio_track: 
	:return: 
	"""
	max_volume, mean_volume = get_volume_info(audio_track)
	print(f"Max Volume = {max_volume} db, Mean Volume = {mean_volume} db")

	command = ['ffmpeg', '-i', str(audio_track), '-vn', '-af',
	           f'aresample=22050,silencedetect=noise={0.4*float(max_volume)+0.6*float(mean_volume)}dB:d=4.0', '-f', 'null',
	           '-']
	output = run_command(command, get_output=True)

	# Parse the silence segments and convert to floating format
	silence_starts = [float(match) + 2.0 for match in
	                  re.findall(r'silence_start: (\d+\.?\d*)', output)]
	silence_ends = [float(match) - 1.0 for match in
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
	                end - start >= 5.0] # at least active 2.0 seconds
	result_duration = sum(end - start for start, end in reserve_segs)
	print(
		f"Will extract {result_duration:.2f}s from {origin_duration:.2f}s, rate={100.0 * result_duration / origin_duration:.2f} %")

	reserve_segs = [(sec_to_ts(range[0]), sec_to_ts(range[1])) for range in
	                reserve_segs]

	with open('_temp_reserve_seg_list.txt', 'w') as file:
		for tup in reserve_segs:
			line = ','.join(tup)  # Join tuple elements with a comma
			file.write(line + '\n')
	return reserve_segs

def process_video(input_video, output_video, audio_track="", seg_list_file="", dry_run=False):
	if not audio_track:
		audio_track = input_video
	origin_duration = get_video_duration(audio_track)
	if origin_duration <= 0:
		print("Invalid video duration.")
		return
	print(f"Original video length is: {origin_duration}s")

	if not seg_list_file:
		print("Calculating segs...")
		reserve_segs = get_reserve_segs(audio_track, origin_duration)
	else:
		print(f"Loading segs from {seg_list_file}")
		with open(seg_list_file, 'r') as file:
			reserve_segs = [line.strip().split(',') for line in file]
			
	print(
		f"Extracted {len(reserve_segs)} highlighted segments: {reserve_segs}")
	if dry_run:
		print("Dry run mode, will stop here before cutting the video into segments")
		return

	seg_files = [''] * len(reserve_segs)
	# ThreadPoolExecutor to cut video into segs, and add their names to the seg_files
	with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()-1) as executor:
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

	concat_command = ['ffmpeg', '-y', '-hide_banner',
	                  #'-loglevel', 'quiet',
	                  '-f', 'concat', '-safe', '0', '-i', str(video_list),
	                  '-c', 'copy',
	                  # '-c:v','libx264',
	                  # '-c:a', 'aac',
	                  str(output_video)]
	run_command(concat_command)
	
	result_duration = get_video_duration(output_video)
	print(
		f"Output highlight video to {output_video}, extract {result_duration:.2f}s from {origin_duration:.2f}s, rate={100.0 * result_duration / origin_duration:.2f} %")

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
	parser.add_argument("-a", "--audio_track", default="",
	                    help="optional, path to the audio track file that has no vocal")
	parser.add_argument("-s", "--seg_list", default="",
	                    help="optional, path to the seg list file, each line is a seg such as ('00:26:51.75', '00:27:5.18')")
	parser.add_argument("-d", "--dry-run", action="store_true",
	                    help="perform a dry run (only calculate the segs) without cutting video")
	args = parser.parse_args()

	# Process starts here
	input = args.input
	if input is None:
		parser.print_usage()
		return
	output = args.output or f"{os.path.splitext(input)[0]}_highlight.mp4"
	audio_track = args.audio_track
	seg_list = args.seg_list
	dry_run = args.dry_run

	process_video(input, output, audio_track, seg_list, dry_run)


if __name__ == "__main__":
	start_time = time.time()  # Record start time
	main()
	end_time = time.time()  # Record end time

	print(f"Total running time: {end_time - start_time:.2f}s")
