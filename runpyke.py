""""""
import argparse
import json
import subprocess
from pathlib import Path
from warnings import warn


def main():
	interpreters = collect_kernel_interpreters()

	parser = argparse.ArgumentParser(
		"runpyke",
		description="direkt kernel program-runner",
	)

	parser.add_argument(
		"kernel",
		type=str
	)

	parser.add_argument(
		"interpreter_argument",
		nargs="*"
	)

	args, pip_args = parser.parse_known_args()

	if args.kernel in interpreters:

		interpreter_path = interpreters[args.kernel]

		run(interpreter_path, pip_args)

	else:
		kernellist = ", ".join(interpreters.keys())
		raise RuntimeWarning(f"Kernel {args.kernel} was not found. There are\n{kernellist}")


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


def run(path: str, arguments: list):
	return subprocess.run([path] + arguments)


if __name__=="__main__":
	try:
		main()
	except Warning as w:
		print(f"Ohh, we ran into a problem: {str(w)}")
		quit(-1)
