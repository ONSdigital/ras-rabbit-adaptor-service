# ras-rabbit-adaptor-service

[![Build Status](https://travis-ci.org/ONSdigital/ras-rabbit-adaptor-service.svg?branch=master)](https://travis-ci.org/ONSdigital/ras-rabbit-adaptor-service) 
[![codecov](https://codecov.io/gh/ONSdigital/ras-rabbit-adaptor-service/branch/master/graph/badge.svg)](https://codecov.io/gh/ONSdigital/ras-rabbit-adaptor-service)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/043810e79dac47759cc661361a8af12b)](https://www.codacy.com/app/ONS/ras-rabbit-adaptor-service?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ONSdigital/ras-rabbit-adaptor-service&amp;utm_campaign=Badge_Grade)

A small service that consumes BRES SEFT messages from a RabbitMQ queue and posts them to the RAS CI service http endpoint.

### Basic Use

Assuming you are executing from inside an activated virtual environment:

###### Install requirements:

    $ make build

###### Run the unit tests:

    $ make test
