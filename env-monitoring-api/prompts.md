# Prompts Utilizados

## 1. Generación inicial de la API

Se generó el contrato base OpenAPI 3.1 para una API REST de monitoreo ambiental IoT.

```text
Necesito un  openapi.yaml  (OpenAPI 3.1) para una API REST de monitoreo ambiental IoT.

Recursos:
Device {id, name, location}
Measurement {id, temperature, humidity, timestamp, device_id}

Endpoints:
GET /devices
POST /devices

GET /devices/{id}/measurements
POST /devices/{id}/measurements -> 201 / 400 / 404

DELETE /devices/{id}/measurements/{measurementId}

Requisitos:
- Definir schemas tipados
- Usar  required 
- Usar  format  donde aplique ( date-time ,  float , etc.)
- Incluir responses de error 400 y 404
- Formato YAML
- Solo definir el contrato OpenAPI, sin implementación
```

---

## 2. Reemplazo de UUID por identificadores numéricos

Se actualizaron los schemas y parámetros reutilizables para usar IDs enteros en lugar de UUIDs.

```text
En  openapi.yaml :

- Reemplazar todos los  type: string  +  format: uuid  por  type: integer  en:
  -  components.parameters.DeviceId 
  -  components.parameters.MeasurementId 
  -  Device.id 
  -  Measurement.id 
  -  Measurement.device_id 

- Actualizar ejemplos UUID por números simples ( 1 ,  2 , etc.)

- Renombrar  {id}  →  {deviceId}  en:
  -  /devices/{id}/measurements 
  -  /devices/{id}/measurements/{measurementId} 

- En  components.parameters.DeviceId , cambiar:
  -  name: id 
  - por  name: deviceId 

Mantener el resto igual.
```

---

## 3. Mejora de estructura y manejo de errores

Se agregó un endpoint individual para dispositivos, descripciones de tags y mejoras en el schema de errores.

```text
agregar endpoint:
- GET /devices/{deviceId}
- usando el parametro reusable deviceId
- response 200 con schema Device
- response 404 usando #/components/responses/NotFound

Agregar description a los tags:
 - Devices
- Measurements

En ErrorResponse, agregar propiedad:
status:
type: integer
e incluirla en required

en el response 204 de DELETE /devices/{deviceId}/measurements/{measurementId} agregar:
content: {}
```

---

## 4. Agregado de metadata y descripciones

Se extendió el schema  Device  con timestamps y estado del dispositivo, además de documentar las operaciones.

```text
En  openapi.yaml  realizar los siguientes cambios:

- En  components.schemas.Device , agregar:

created_at:
  type: string
  format: date-time
  description: Device creation timestamp

status:
  type: string
  description: Current device status
  enum:
    - online
    - offline
    - maintenance

- Agregar  created_at  y  status  en  required  del schema  Device 

- Agregar ejemplos apropiados para ambos campos

- Agregar  description  en todas las operations ( get ,  post ,  delete ) dentro de  paths , describiendo brevemente qué hace cada endpoint

Mantener el resto del archivo igual.
```

---

## 5. Endpoint para eliminar dispositivos

Se agregó un endpoint RESTful para eliminar dispositivos.

```text
En  openapi.yaml , agregar un nuevo endpoint sin modificar la estructura existente ni reescribir el archivo completo.

Nuevo endpoint:
-  DELETE /devices/{deviceId} 

Requisitos:
- Usar el parámetro reusable  DeviceId 
- Tag:  Devices 
-  operationId: deleteDevice 
- Response  204  con:

content: {}

- Response  404  usando  #/components/responses/NotFound 

Mantener el resto del archivo sin cambios.
```