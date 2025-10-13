{{/*
Expand the name of the chart.
*/}}
{{- define "kaimen-backend.name" -}}
{{ .Chart.Name }}
{{- end }}

{{/*
Create a fullname using the release name and the chart name.
*/}}
{{- define "kaimen-backend.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "kaimen-backend.labels" -}}
app.kubernetes.io/name: {{ .Release.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
