# Common Errors and their workarounds

## Docker access denied
**Symptoms:**

```
docker: Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: ...
connect: permission denied.
```
**Cause**

You need to be part of the Docker user group

**Remedy:**

```
sudo usermod -aG docker <username>
```
You will need to logout and log back in to obtain the group membership. To check it:
```
$ id
uid=1001(dash) gid=1001(dash) groups=1001(dash),27(sudo),998(docker)
```
