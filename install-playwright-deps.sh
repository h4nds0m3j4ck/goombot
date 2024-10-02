#!/bin/bash

apt-get update && apt-get install -y \
  libgstreamer-gl1.0-0 \
  libgstreamer-plugins-bad1.0-0 \
  libenchant-2-2 \
  libsecret-1-0 \
  libmanette-0.2-0 \
  libgles2-mesa
