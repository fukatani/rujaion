# Contribute Guide

## Contributon

Not only sending Pull Requests, feature requests and bug reports are welcome!

## pull requests

PR is always welcome.

However, please note that PR is not always merged as it is.
To improve PR quality, reviewers may ask you change requests.

-   Write code easy to understand.
    -   Don't make diff which is unnecessary for the purpose of PR.
    -   Split commits appropriately.
    -   Comment on the code where you are not confident of.
-   If you want to add a feature, it would be better to discuss on issue before writing code.
    -   because your feature is not always merged.

## formatter

Please format your code by `black` before sending PR.

``` sh
$ black .
```

## CI

Currently, travis CI will check the code is formatted or not only.

