# -*- coding: utf-8 -*-
client {
    Name = "{{ fqdn }}-fd"
    Address = {{ fqdn }}
    FDPort = 9102
    Catalog = PrimaryCatalog
    Password = "{{ passhash }}"
    File Retention = 40 days
    Job Retention = 1 months
    AutoPrune = yes
    Maximum Concurrent Jobs = 10
    Heartbeat Interval = 300
}

Job {
    Name = "{{ fqdn }}-Job"
    Type = Backup
    Level = Incremental
    FileSet = "{{ fileset }}"
    Client = "{{ fqdn }}-fd"
    Storage =  "{{ storage_node }}"
    Pool = "{{ pool }}"
    Schedule = "{{ schedule }}"
    Messages = Standard
    Priority = 10
    Write Bootstrap = "/var/db/bacula/%c.bsr"
    Maximum Concurrent Jobs = 10
    Reschedule On Error = yes
    Reschedule Interval = 1 hour
    Reschedule Times = 1
    Max Wait Time = 90 minutes
    Cancel Lower Level Duplicates = yes
    Allow Duplicate Jobs = no
}

Job {
    Name = "{{ fqdn }}-Restore"
    Type = Restore
    Client= "{{ fqdn }}-fd"
    FileSet="{{ fileset }}"
    Storage = {{ storage_node }}
    Pool = "{{ pool }}"
    Messages = Standard
    Where = /tmp
}
