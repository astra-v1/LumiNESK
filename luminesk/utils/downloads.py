import httpx

from luminesk.core.messages import t
from luminesk.core.registry import CoreProvider, GitHubRelease, Jenkins, Maven
from luminesk.utils.download_models import CoreDownloadInfo
from luminesk.utils import github_releases, jenkins, maven


def get_availability_check_url(core: CoreProvider) -> str:
	if isinstance(core, Maven):
		return maven.get_metadata_url(core)

	if isinstance(core, Jenkins):
		return jenkins.get_build_info_url(core)

	if isinstance(core, GitHubRelease):
		return github_releases.get_release_api_url(core)

	raise ValueError(
		t(
			"downloads.unsupported_provider_type",
			type_name=type(core).__name__,
			core_id=core.id,
		)
	)


def get_latest_download_info(core: CoreProvider, client: httpx.Client | None = None) -> CoreDownloadInfo:
	if isinstance(core, Maven):
		return maven.get_latest_download_info(core, client=client)

	if isinstance(core, Jenkins):
		return jenkins.get_latest_download_info(core, client=client)

	if isinstance(core, GitHubRelease):
		return github_releases.get_latest_download_info(core, client=client)

	raise ValueError(
		t(
			"downloads.unsupported_provider_type",
			type_name=type(core).__name__,
			core_id=core.id,
		)
	)


def get_latest_download_url(core: CoreProvider, client: httpx.Client | None = None) -> str:
	return get_latest_download_info(core, client=client).url
