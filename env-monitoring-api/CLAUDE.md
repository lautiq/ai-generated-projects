# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

This repository contains only an **OpenAPI 3.1 contract** (`openapi.yaml`) for an IoT environmental monitoring REST API. There is no implementation — no server, no database, no tests. The deliverable is the YAML specification itself.

## Validation

Paste the contents of `openapi.yaml` into [https://editor.swagger.io/](https://editor.swagger.io/) to validate and interactively explore the contract. There is no local tooling or CLI configured.

## API design conventions

- **IDs are integers** (`type: integer`), not UUIDs.
- **Measurements are nested** under devices: all measurement endpoints live under `/devices/{deviceId}/measurements`.
- **Reusable components** — path parameters (`DeviceId`, `MeasurementId`), error responses (`BadRequest`, `NotFound`), and all schemas are defined under `components` and referenced with `$ref`. Never inline what already exists in `components`.
- **Error shape** is always `ErrorResponse` (`status`, `error`, `message`), referenced via `$ref: '#/components/responses/BadRequest'` or `NotFound`.
- **`additionalProperties: false`** is set on every request/response schema — maintain this on any new schema.
- **`content: {}`** is required on all `204` responses.
- Device `status` is an enum: `online | offline | maintenance`.
- Humidity is bounded: `minimum: 0`, `maximum: 100`.
- Temperature and humidity use `format: float`.
- Timestamps use `format: date-time` (ISO 8601).

## Endpoints summary

| Method | Path | Description |
|--------|------|-------------|
| GET | `/devices` | List all devices |
| POST | `/devices` | Create a device |
| GET | `/devices/{deviceId}` | Get a device |
| DELETE | `/devices/{deviceId}` | Delete a device |
| GET | `/devices/{deviceId}/status` | Get device status |
| GET | `/devices/{deviceId}/measurements` | List measurements |
| POST | `/devices/{deviceId}/measurements` | Create a measurement |
| DELETE | `/devices/{deviceId}/measurements/{measurementId}` | Delete a measurement |
