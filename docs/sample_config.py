from crabpot import Pot

pot = Pot()
pot.name = "ElectronBackgrounds"
pot.defaults["crab_config"] = "config_2022_cfg.py"

channels = [
    "ZtoEleProbeTrk",
    "ZtoEleProbeTrkWithFilter", 
    "ZtoEleProbeTrkWithSSFilter",
    "ZtoEleProbeTrkWithFilterLoose"
]

version_map = {
    "2023C": ["v1", "v2", "v3", "v4"],
    "2023D": ["v1", "v2"]
}

# 2023 stuff
for era, versions in version_map.items()
    for channel in channels:
        for version in versions:
            crab = pot.create_crab(f"{era}_{version}_{channel}_NLayers")

            crab.add_template_file("crab_config.py.jinja", is_crab_config=True)
            crab.add_template_file("cmssw_pset_cfg.py.jinja")
            crab.add_template_file("osu_cfg.py.jinja")

            crab.tags = {"era":era, "channel": f"{channel}NLayers"}

            crab.substitutions = {
                "filelist": f"ZtoEleProbeTrk_{era}_{version}.txt",
                "channel": f"getNLayersChannelVariations(\"{channel}\")"
                "era": era
            }

"""
            if channel != "ZtoEleProbeTrk"
                crab = pot.create_crab(f"{era}_{version}_{channel}")
                crab.tags = tags
                crab.overrides = {
                    "filelist": f"ZtoEleProbeTrk_{era}_{version}.txt",
                    "channel": f"[channel]"
                }
"""
