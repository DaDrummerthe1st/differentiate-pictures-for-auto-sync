# Fix docker stats container-name bug, record real detector smoke-test results

`DEPLOYMENT.md`'s smoke-test `docker stats detector` used the Compose service name, not the real
container name Compose v2 actually assigns — fixed to resolve it via `ps -q`. Ran the smoke test for
real against `/tank/momfiles/Florida1/Florida/1/IMGP0128.JPG` (both quality trio and YuNet face
detection confirmed working; 402MiB/768MiB baseline RSS noted for the benchmarking work ahead) and
recorded the result. Added `CVE`/`Dependabot`/`uv` and five vulnerability-class terms (`DoS`,
quadratic-time parsing, unbounded buffering, parameter smuggling, arbitrary-file-write) to the
glossary, prompted by explaining the `python-multipart` CVE bumps in chat.

- **Doc size**: `documentation/GLOSSARY.md` +3436 chars, `documentation/photo-server/DEPLOYMENT.md` +1037 chars.
