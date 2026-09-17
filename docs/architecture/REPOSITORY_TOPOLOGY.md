# Topologi Repository

```text
alos-web / ARA / GIIVEPRO
             |
             | API publik
             v
       alos-backend  <---- data, kebijakan, dan keputusan authoritative
             |
             | kontrak run internal
             v
         genesis-ai  ----> ModelGateway ----> provider model yang disetujui
             |
             | ToolRequest
             v
  alos-backend ToolExecutor

alos-contracts ----> kontrak kanonis yang digunakan semua repository
alos-infra     ----> melakukan deployment/konfigurasi implementasi, tidak mendefinisikan ulang kontrak
```

`alos-contracts` menjadi dependency bagi implementasi dan tidak pernah bergantung pada implementasi tersebut. ARA dan GIIVEPRO masuk melalui boundary otoritas backend yang sama seperti client lainnya.
