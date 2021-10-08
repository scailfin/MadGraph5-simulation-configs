# Running on NCSA DGX


```console
docker pull scailfin/madgraph5-amc-nlo-centos:mg5_amc3.2.0
```

```
docker run --rm -ti scailfin/madgraph5-amc-nlo-centos:mg5_amc3.2.0
```

Note that Docker is running as `root` so if you want to follow along with its CPU and memeory useage instead of running

```console
$ htop -u $USER
```

you need to run

```console
$ htop -u root
```
