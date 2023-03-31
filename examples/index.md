---
layout: default
title: Example Scripts
nav_order: 3
has_children: False
---

The links below give examples of how to use the program.

# Example command to run DRIVE:
---
The following command assumes that you have either installed DRIVE using pip or that you have installed it from github. The following command will show you how to call it if you install DRIVE using pip. This example command has only the required arguments.

```bash
drive -i {input ibd filepath} -f {ibd program format} -t {chromosome position to cluster around} -o {output filepath}
```

{: .alternative }
If you installed DRIVE from github then you can replace the 'drive' portion with "python /path_to_drive.py". The rest of the command will be the same.