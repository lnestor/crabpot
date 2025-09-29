from CRABClient.UserUtilities import config
config = config()

{{ crabpot_reserved }}

config.JobType.pluginName = "Analysis"
config.JobType.psetName = {{ configCMSSW }}
config.JobType.maxMemoryMB = {{ maxMemory }}

config.Data.inputDataset = {{ dataset }}
config.Data.inputDBS = {{ inputDBS }}
config.Data.splitting = "FileBased"
config.Data.unitsPerJob = 1
config.Data.outLFNDirBase = {{ outputDir }}

config.Site.storageSite = {{ storageSite }}
