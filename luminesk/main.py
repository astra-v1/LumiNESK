from importlib.metadata import PackageNotFoundError, version


def _detect_version() -> str:
	try:
		return version("luminesk")
	except PackageNotFoundError:
		return "0.0.0"


__version__ = _detect_version()


def main() -> None:
	from luminesk.cli.main import app

	app()

if __name__ == "__main__":
	main()
