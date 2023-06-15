"""This script will show you the size of installed python packages.

Because our instances are limited with regards to disk space, it's useful to
keep a handle on dependency size.
"""
import os
import pkg_resources


def calc_container(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


dists = [d for d in pkg_resources.working_set]

lines = []
for dist in dists:
    try:
        path = os.path.join(dist.location, dist.project_name)
        size = calc_container(path)
        mb = round(size / 1000 / 1000, 2)
        lines.append((size, f"{dist}: {mb} MB"))
    except OSError:
        '{} no longer exists'.format(dist.project_name)

lines.sort(key=lambda x: x[0], reverse=True)
for line in lines:
    print(line[1])

mb = round(sum([line[0] for line in lines]) / 1000 / 1000, 2)
print(f'Total: {mb} MB')
