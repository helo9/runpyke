""""""
import argparse
import json
import subprocess
from pathlib import Path
from warnings import warn

def collect_kernel_interpreters():

	try:
		res = subprocess.run(
			"jupyter kernelspec list --json".split(),
			capture_output=True
		)
	except Exception as e:
		raise RuntimeError("Failed running kernelspec request, is the jupyter cli installed and available?") from e

	if res.returncode != 0:
		raise RuntimeError(f"Requesting kernelspec resulted in error code {res.returncode}")

	try:
		kernel_specs = json.loads(res.stdout)["kernelspecs"]
	except:
		raise Exception("Could not parse kernelspec.")

	interpreters: dict[str, str] = {}

	for name, spec in kernel_specs.items():
		try:
			interpreters[name] = spec["spec"]["argv"][0]
		except KeyError as e:
			warn(f"Could not determine interpreter path for kernel {name}")
			continue

	return interpreters


def locate_pip(interpreter_path):
	python_binary_path = Path(interpreter_path).parent

	pip_path = (python_binary_path /"pip")

	if pip_path.exists == False:
		raise FileNotFoundError("Could not find pip in interpreter folder")

	return pip_path


def run_pip(path: str, arguments: list):
	subprocess.run([path] + arguments)


def main():
	interpreters = collect_kernel_interpreters()

	parser = argparse.ArgumentParser(
		"direkt kernel program-runner",
	)

	parser.add_argument(
		"kernel",
		type=str
	)

	args, pip_args = parser.parse_known_args()

	if args.kernel in interpreters:

		interpreter_path = interpreters[args.kernel]

		pip_path = locate_pip(interpreter_path)

		run_pip(pip_path, pip_args)


if __name__=="__main__":
	main()
