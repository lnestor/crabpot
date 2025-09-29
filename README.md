# Crabpot

Crabpot manages group of CRAB jobs together. Often times doing high energy research at CMS you have to run multiple similar CRAB jobs on different datasets, with different cuts, etc. Crabpot allows you to treat related CRAB jobs as a single unit, reducing errors and increasing simplicity.

# How it Works

In Crabpot, you define "pots" of related CRAB jobs. 

# Installation

# Common Commands

`create` - Creates a new pot with a given name.

`submit` - Submits all unsubmitted CRAB jobs in a pot.

`status` - Prints the status of all CRAB jobs in a pot.

`resubmit` - Resubmits failed CRAB jobs in a pot.

`add` - Add a new CRAB job to a pot.

# How it Works

Crabpot stores data in a `.crabpot` directory in your current directory.
