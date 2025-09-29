from CRABClient.UserUtilities import config

config = config()

config.General.requestName = "{{ crabpot_name }}"
config.General.workArea = "{{ crabpot_work_area }}"

config.JobType.psetName = "sample_cfg.py"

config.Data.inputDataset = "{{ dataset }}"
