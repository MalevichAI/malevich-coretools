from typing import Optional


def check_profile_mode(profile_mode: Optional[str]) -> None:  # noqa: ANN202
    assert profile_mode in [None, "no", "all", "time", "df_info", "df_show"], f"wrong profile_mode: {profile_mode}"
