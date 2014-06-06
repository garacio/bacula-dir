# -*- coding: utf-8 -*-
Director {
  Name = bacula-dir
  Password = "{{ passhash }}"
}

FileDaemon {
  Name = "{{ fqdn }}-fd"
  FDport = 9102
  WorkingDirectory = /var/lib/bacula
  Pid Directory = /var/run/bacula
  Maximum Concurrent Jobs = 10
  FDAddress = 0.0.0.0
  Heartbeat Interval = 1 Minute
}

Messages {
  Name = Standard
  director = bacula-dir = all, !skipped, !restored
}
