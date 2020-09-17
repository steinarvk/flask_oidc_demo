# What is this?

It's a Python demo app that allows login through an OIDC identity provider.
It's a working example of `flask-oidc` with a custom callback, suitable
for writing a stateless app.

## Who wrote this and why?

I (@steinarvk) wrote this as a test app while setting up a Keycloak server.

## Can I use it?

Sure, it's MIT licensed.

However, it's just a demo app and it's not necessarily likely to be
terribly useful to use the code wholesale. I make no particular claim that
this demo app shows the ideal way to do things. It's more likely to be
useful as an example or as a testing app if you're trying to set
up `flask-oidc` or Keycloak.

# How to deploy the demo app

## Set up a domain

You need to have a way to make a Docker container (which serves HTTP on
port 80) serve HTTPS on a reachable domain name. This could be a reverse
proxy and `docker run`, or it could be some sort of cloud service
(e.g. Cloud Run).

The rest of the instructions assume that you'll be able to serve
HTTPS pages under some domain, referred to as `${APP_URL}`.

## Set up an identity provider supportin OIDC

You need an identity provider that supports OIDC.

This demo app was tested with (and in fact developed for the purpose of
testing) Keycloak: https://keycloak.org

## Perform dynamic client registration

You need to register your new app with your OIDC provider, to obtain a
file (`client_secrets.json`) containing client secrets.

The simplest way to do this is with the `oidc-register` tool.

```
$ export PROVIDER_URL=https://keycloak.example.com/auth/realms/myrealm
$ export APP_URL=https://flask-oidc-demo.example.com
$ mkdir -p secret
$ cd secret
$ oidc-register "$PROVIDER_URL" "$APP_URL"
```

## Configure your provider

You may need to allow `${APP_URL}/callback` as a redirect URL.

## Build the Docker container and deploy it

`secret/client_secrets.json` should be copied into the Docker container
or mounted as a volume. By default it is copied into the container.
It is loaded by default from `/app/client_secrets.json`.

Set the following environment variables:
  - `FLASK_SECRET_KEY` to a randomly-generated hexadecimal key.
    (One way to generate one is:
     `head -c 100 /dev/random | sha256sum - | cut -d' ' -f 1`)
  - `APP_BASE_URL` to e.g.: https://flask-oidc-demo.example.com

## Test the demo

Visit `${APP_URL}`. The index page doesn't require login, but the
"secret" pages will require it.
