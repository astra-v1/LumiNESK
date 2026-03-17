from typing import ClassVar
from pydantic import BaseModel, ConfigDict


class CoreProvider(BaseModel):
	model_config = ConfigDict(frozen=True)

	id: str
	name: str
	description: str
	url: str
	config_file: str = "server.properties"

	def get_metadata_url(self) -> str:
		return self.get_availability_check_url()

	def get_availability_check_url(self) -> str:
		from luminesk.utils.downloads import get_availability_check_url

		return get_availability_check_url(self)

	def get_latest_download_url(self) -> str:
		from luminesk.utils.downloads import get_latest_download_url

		return get_latest_download_url(self)

class Maven(CoreProvider):
	group_id: str
	artifact_id: str
	classifier: str | None = None
	is_snapshot: bool = False

class Jenkins(CoreProvider):
	pass

class GitHubRelease(CoreProvider):
	release_file: str

class CoreRegistry:

	_cores: ClassVar[dict[str, CoreProvider]] = {
		"nukkit": Maven(
			id="nukkit",
			name="Nukkit",
			description="Original Minecraft server core.",
			url="https://repo.opencollab.dev/maven-snapshots",
			group_id="cn.nukkit",
			artifact_id="nukkit",
			is_snapshot=True
		),
		"pnx": Maven(
			id="pnx",
			name="PowerNukkitX",
			description="Advanced core with support for newer blocks and entities.",
			group_id="org.powernukkitx",
			artifact_id="server",
			url="https://repo.powernukkitx.org/releases",
			classifier="all",
			is_snapshot=True,
			config_file="pnx.yml"
		),
		"nukkit-mot": Jenkins(
			id="nukkit-mot",
			name="Nukkit-MOT",
			description="Core with multi-version MCBE support and a strong vanilla focus.",
			url="https://motci.cn/job/Nukkit-MOT/job/master"
		),
		"lumi-gh": GitHubRelease(
			id="lumi-gh",
			name="Lumi (GitHub Release)",
			description="Nukkit-MOT-based core focused on optimization and customization.",
			url="https://github.com/KoshakMineDEV/Lumi",
			release_file="Lumi-*.jar"
		),
		"lumi": Maven(
			id="lumi",
			name="Lumi",
			description="Nukkit-MOT-based core focused on optimization and customization.",
			group_id="com.koshakmine",
			artifact_id="Lumi",
			url="https://repo.luminiadev.com/snapshots"
		),
	}

	@classmethod
	def get_all(cls) -> list[CoreProvider]:
		return list(cls._cores.values())

	@classmethod
	def get_by_id(cls, core_id: str) -> CoreProvider | None:
		return cls._cores.get(core_id.lower())

	@classmethod
	def get_ids(cls) -> list[str]:
		return list(cls._cores.keys())

	@classmethod
	def has(cls, core_id: str) -> bool:
		return core_id.lower() in cls._cores

registry = CoreRegistry()
