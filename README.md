# Gardening App Documentation

## Inhaltsverzeichnis
1. [Motivation und Zweck der Gardening App](#1-motivation-und-zweck-der-gardening-app)
2. [Gesamtarchitektur](#2-gesamtarchitektur)
   1. [Backend](#21-backend)
   2. [Data-Tier](#22-data-tier)
3. [Backend](#3-backend)
   1. [Datensatzaufbereitung](#31-datensatzaufbereitung)
   2. [Wetterdaten Handling](#32-wetterdaten-handling)
   3. [Suitability Score](#33-suitability-score)
   4. [Datenbankhandling](#34-datenbankhandling)
   5. [REST API](#35-rest-api)
   6. [Swagger-UI und API-Dokumentation](#36-swagger-ui-und-api-dokumentation)
   7. [Mehrwert des Backends](#37-mehrwert-des-backends)
4. [Data-Tier](#4-data-tier)
   1. [Datenmodell (models.py)](#41-datenmodell-modelspy)
   2. [Wetterdaten](#42-wetterdaten)
5. [Frontend](#5-frontend)
   1. [Visualisieren der Wetterdaten](#51-visualisieren-der-wetterdaten)
   2. [Handling von LLM Prompting und Prompt Engineering](#52-handling-von-llm-prompting-und-prompt-engineering)
   3. [Begründung für LLM Handling im Frontend](#53-begründung-für-llm-handling-im-frontend)
6. [Deployment mit Kubernetes](#6-deployment-mit-kubernetes)
7. [Abdeckung der Anforderungen](#7-abdeckung-der-anforderungen)
8. [Quellen](#8-quellen)

## 1. Motivation und Zweck der Gardening App
Die Gardening App wurde entwickelt, um Hobbygärtnern eine einfache und effektive Möglichkeit zu bieten, den optimalen Aussaatzeitpunkt für verschiedene Pflanzenarten basierend auf eigenen Wetterdaten zu bestimmen. Die App führt dabei eine grobe, aber dennoch zuverlässige Analyse durch, die es den Benutzern ermöglicht, fundierte Entscheidungen für ihre Gartenplanung zu treffen.

Ein besonderer Vorteil der App liegt in der Nutzung der EcoCrop-Datenbank, die von der UN entwickelt wurde und eine umfassende Sammlung klimatischer Anforderungen für eine Vielzahl von Pflanzenarten enthält. Die Komplexität des vollständigen EcoCrop-Modells übersteigt jedoch die Anforderungen vieler Benutzer und ist aufgrund fehlender, exakt passender Daten für das Modell oft nicht anwendbar. Daher wurde die Berechnung der Suitability Scores vereinfacht, um eine benutzerfreundliche und dennoch informative Lösung zu bieten, die speziell auf die Bedürfnisse von Hobbygärtnern zugeschnitten ist.

Ziel der App ist es, die Gartenplanung zu optimieren, indem eine einfache, aber effektive Analyse der klimatischen Bedingungen und deren Einfluss auf das Pflanzenwachstum ermöglicht wird.

## 2. Gesamtarchitektur
### 2.1 Backend
Das Backend der Gardening App ist darauf ausgelegt, die Hauptlogik der Anwendung zu handhaben, einschließlich der Verarbeitung von Pflanzendaten und Wetterinformationen, sowie der Berechnung der Eignungsbewertung (Suitability Score). Es umfasst mehrere zentrale Komponenten, die nachfolgend erläutert werden.

### 2.2 Data-Tier
Das Data-Tier speichert alle erforderlichen Daten, einschließlich Pflanzendaten und historischen Wetterinformationen, die für die Eignungsbewertung erforderlich sind. Die Daten werden in einer PostgreSQL-Datenbank verwaltet.

## 3. Backend
### 3.1 Datensatzaufbereitung
Die EcoCrop-Datenbank, die umfangreiche Informationen zu den klimatischen Anforderungen vieler Pflanzen enthält, wird vor der Nutzung in der App aufbereitet. Diese Aufbereitung umfasst die Bereinigung und Transformation der Daten, um sicherzustellen, dass sie den Anforderungen der App entsprechen.

### 3.2 Wetterdaten Handling
Das Backend ruft historische Wetterdaten von der Open Meteo API ab und verarbeitet diese, um sie in die Berechnung des Suitability Scores einfließen zu lassen.

### 3.3 Suitability Score
Der Suitability Score wird basierend auf den abgerufenen Wetterdaten und den Anforderungen der Pflanzenarten berechnet. Dabei wird eine vereinfachte Methode verwendet, um eine schnelle und dennoch aussagekräftige Bewertung zu ermöglichen.

### 3.4 Datenbankhandling
Die Anwendung überprüft die Datenbank auf vorhandene Einträge und lädt die erforderlichen Daten aus der CSV-Datei, wenn Einträge fehlen. Dies gewährleistet, dass die Datenbank stets die notwendigen Informationen für die Berechnungen enthält.

### 3.5 REST API
Die REST API des Backends stellt verschiedene Endpunkte bereit, über die das Frontend auf die Pflanzendaten, Wetterinformationen und die berechneten Suitability Scores zugreifen kann.

### 3.6 Swagger-UI und API-Dokumentation
Die REST API des Backends ist automatisch mittels einer **Swagger-UI** dokumentiert. Diese bietet eine umfassende Übersicht über die verfügbaren API-Endpunkte sowie die dazugehörigen Request- und Response-Formate. Entwickler und Nutzer können die API-Endpunkte direkt in der Benutzeroberfläche testen, was die Integration und das Verständnis der API erleichtert.

Die Swagger-Dokumentation kann unter folgendem Link aufgerufen werden:  
[Swagger Dokumentation der Gardening API](https://plantsapi-13434.edu.k8s.th-luebeck.dev/docs)

### 3.7 Mehrwert des Backends
Das Backend der Gardening App spielt eine zentrale Rolle bei der Bereitstellung der Kernfunktionalitäten der Anwendung und stellt damit einen wesentlichen Mehrwert für die App dar. Zu den wichtigsten Mehrwerten des Backends gehören:

1. **Verarbeitung großer Datensätze**:  
   Das Backend verarbeitet die umfangreichen Pflanzendaten der EcoCrop-Datenbank und speichert diese in einer PostgreSQL-Datenbank. Diese Pflanzendaten werden für die Berechnung der optimalen Anbaubedingungen verwendet.

2. **Integration externer Datenquellen**:  
   Durch die Integration von Wetterdaten (über die Open Meteo API) ermöglicht das Backend die Echtzeitberechnung der optimalen Pflanzbedingungen, die auf den aktuellen klimatischen Gegebenheiten basieren.

3. **Berechnung des Suitability Scores**:  
   Das Backend berechnet basierend auf den Pflanzendaten und den historischen Wetterdaten einen **Suitability Score**, der anzeigt, wie gut die aktuellen Bedingungen für das Wachstum einer bestimmten Pflanze sind. Diese Berechnung erfolgt in Echtzeit und wird über die API dem Frontend zur Verfügung gestellt.

4. **Bereitstellung der API-Endpunkte**:  
   Über die **REST API** des Backends können Entwickler und das Frontend einfach auf die Pflanzendaten und die Suitability Score-Berechnungen zugreifen. Dies ermöglicht eine flexible und dynamische Nutzung der Daten und Berechnungen, ohne dass das Frontend selbst die Datenverarbeitung übernehmen muss.

5. **Automatisierte Dokumentation**:  
   Dank der in FastAPI integrierten Swagger-UI ist die API automatisch dokumentiert, was die Nutzung und Integration der API für Entwickler vereinfacht. So wird sichergestellt, dass alle verfügbaren Endpunkte und ihre Funktionalitäten transparent und verständlich dargestellt sind.

6. **Skalierbarkeit und Erweiterbarkeit**:  
   Durch die Implementierung als REST API kann das Backend einfach skaliert und bei Bedarf erweitert werden, um zusätzliche Funktionalitäten oder Datenquellen zu integrieren. Diese Flexibilität ist besonders wichtig, um das System an neue Anforderungen anzupassen.

### 3.8 Zusammenfassung
Das Backend der Gardening App bietet einen erheblichen Mehrwert, da es die Kernlogik der Anwendung übernimmt, externe Daten integriert und den Suitability Score in Echtzeit berechnet. Ohne das Backend wäre die Gardening App nicht in der Lage, die benötigten Daten zu verarbeiten oder den Nutzern präzise Empfehlungen für den Pflanzenanbau zu geben. Durch die automatische Dokumentation der API über Swagger und die Bereitstellung über Kubernetes ist das Backend sowohl für Entwickler als auch für die Endnutzer optimal zugänglich und nutzbar.

## 4. Data-Tier
### 4.1 Datenmodell (models.py)
Das Datenmodell der App basiert auf SQLAlchemy und definiert die Struktur der in der PostgreSQL-Datenbank gespeicherten Pflanzendaten.

### 4.2 Wetterdaten
Die Wetterdaten werden von der Open Meteo API bezogen und in der Datenbank gespeichert, um sie für die Berechnung der Suitability Scores verfügbar zu machen.

## 5. Frontend
### 5.1 Visualisieren der Wetterdaten
Das Frontend visualisiert die historischen Wetterdaten der letzten 30 Tage in einem anschaulichen Diagramm, um den Benutzern ein besseres Verständnis der klimatischen Bedingungen zu ermöglichen.

### 5.2 Handling von LLM Prompting und Prompt Engineering
Die App nutzt LLMs zur Erstellung benutzerfreundlicher und personalisierter Berichte. Dies erfolgt durch Prompt Engineering, das sicherstellt, dass die Ausgaben der LLMs den Anforderungen der Benutzer entsprechen.

### 5.3 Begründung für LLM Handling im Frontend
Das Handling der LLMs im Frontend ermöglicht eine unmittelbare Interaktion mit den Benutzern und eine dynamische Anpassung der Ausgaben, was zu einer verbesserten Nutzererfahrung führt.

## 6. Deployment mit Kubernetes

Das Deployment der Gardening App erfolgt vollständig automatisiert und containerisiert auf einer Kubernetes-Plattform, was die Skalierbarkeit und Flexibilität der App gewährleistet. Dieser Abschnitt beschreibt die Architektur des Deployments, die verwendeten Komponenten sowie deren Zusammenspiel innerhalb der Kubernetes-Umgebung.

### 6.1 Architekturübersicht

Die Gardening App besteht aus drei Hauptkomponenten: dem Frontend, dem Backend und dem Data-Tier (PostgreSQL). Alle Komponenten sind containerisiert und werden in einem Kubernetes-Cluster ausgeführt, wobei der Betrieb durch automatisierte Continuous Deployment-Pipelines ermöglicht wird. Die Kubernetes-Ressourcen werden über Kubernetes-Manifeste beschrieben und mittels GitLab CI/CD automatisch bereitgestellt.

Das folgende Diagramm zeigt die Gesamtarchitektur der App in der Kubernetes-Umgebung:

![Gardener Kubernetes Architektur](Gardener%20Kubernetes%20Architektur.png)

### 6.2 Komponenten

1. **Frontend**:  
   Das Frontend basiert auf Streamlit und stellt die Benutzeroberfläche bereit, über die der Endnutzer interagiert. Es empfängt Benutzeranfragen über einen Webbrowser, visualisiert Daten und kommuniziert mit dem Backend über API-Calls. Das Frontend wird über einen Kubernetes-Service bereitgestellt und ist durch einen Ingress-Controller von außen zugänglich. Die Ingress-Rules leiten die HTTP-Anfragen an den entsprechenden Service im Cluster weiter.

2. **Backend (API/Business-Logic)**:  
   Das Backend der Gardening App ist verantwortlich für die Hauptlogik der Anwendung, einschließlich der Verarbeitung von Pflanzendaten, dem Abruf von Wetterdaten und der Berechnung der Suitability Scores. Es kommuniziert mit dem PostgreSQL-Data-Tier, um Pflanzendaten zu speichern und abzurufen, und stellt API-Endpunkte für das Frontend bereit. Auch das Backend wird über einen Kubernetes-Service bereitgestellt und über einen eigenen Ingress von außen erreichbar gemacht.

3. **Data-Tier (PostgreSQL)**:  
   Das PostgreSQL-Datenbanksystem dient als persistent Speicher für alle relevanten Pflanzendaten. Diese Komponente ist nicht öffentlich zugänglich und kommuniziert nur mit dem Backend innerhalb des Clusters. Der Datenbestand wird durch ein Persistent Volume (PVC) gesichert, sodass die Daten auch nach einem Neustart des Pods erhalten bleiben.

### 6.3 Kubernetes-Ressourcen

- **Deployments**:  
  Sowohl das Frontend, das Backend als auch der PostgreSQL-Dienst sind als Kubernetes-Deployments konfiguriert, um sicherzustellen, dass die Pods bei Bedarf automatisch skaliert und wiederhergestellt werden. Die Deployments legen fest, wie viele Replikate der jeweiligen Komponente zu jedem Zeitpunkt bereitgestellt werden sollen.
    - **Frontend-Deployment**: Es werden drei Replikate der Streamlit-App betrieben, um eine hohe Verfügbarkeit und Skalierbarkeit zu gewährleisten.
    - **Backend-Deployment**: Auch das Backend besteht aus drei Replikaten, sodass Anfragen parallel verarbeitet und die Last verteilt werden können.
    - **PostgreSQL-Deployment**: Da es sich bei der Datenbank um einen stateful Service handelt, wird lediglich ein Pod bereitgestellt, der mit einem Persistent Volume verbunden ist, um die Daten zu speichern.

- **Services**:  
  Jedes Deployment ist mit einem entsprechenden Kubernetes-Service verbunden, der als interner Load Balancer fungiert. Der Service sorgt dafür, dass die Kommunikation zwischen den Komponenten auch bei veränderten IP-Adressen der Pods stabil bleibt.
    - **Backend-Service**: Verbindet das Backend mit dem PostgreSQL-Service.
    - **Frontend-Service**: Stellt sicher, dass das Frontend mit dem Backend kommunizieren kann.

- **Ingress**:  
  Der Ingress-Controller verwaltet den externen Zugriff auf die App. Zwei separate Ingress-Routen werden konfiguriert:
    - Eine Route für das Frontend unter der Subdomain `gardener-[CI_PROJECT_ID].edu.k8s.th-luebeck.dev`.
    - Eine weitere Route für das Backend unter der Subdomain `plantsapi-[CI_PROJECT_ID].edu.k8s.th-luebeck.dev`.

- **Persistent Volume Claims (PVC)**:  
  Für den PostgreSQL-Datenbankdienst wird ein Persistent Volume verwendet, um die Daten persistent zu speichern. Der entsprechende Volume-Claim stellt sicher, dass der Speicher auch bei Neustarts des Pods erhalten bleibt.

### 6.4 Anpassungen der Deployment Pipeline

Die App wird im Rahmen einer Continuous Deployment Pipeline bereitgestellt, die auf GitLab CI/CD basiert. Diese Pipeline übernimmt den vollständigen Prozess vom Erstellen der Docker-Images über das Hochladen in die Registry bis hin zur Bereitstellung der Ressourcen im Kubernetes-Cluster. Der Deployment-Prozess wurde so angepasst, dass die App automatisch skaliert werden kann und auf Änderungen schnell reagiert. Dies umfasst:
- **Automatisierte Bereitstellung der Container-Images**: Jedes Mal, wenn neue Änderungen in das GitLab-Repository gepusht werden, wird ein neues Docker-Image erstellt und in die Registry gepusht. Anschließend werden die Kubernetes-Ressourcen automatisch aktualisiert.
- **Erstellen von Secrets**: Während der Pipeline wird ein Docker-Registry-Secret erstellt, damit Kubernetes die neuesten Images aus der Registry laden kann.
- **Persistent Storage**: Für den PostgreSQL-Dienst wird ein Persistent Volume Claim konfiguriert, sodass die Daten auch nach Neustarts verfügbar bleiben.
- **Skalierung und Wiederherstellung**: Die Verwendung von Kubernetes-Deployments ermöglicht es, dass die Anzahl der Replikate bei Lastanstieg skaliert werden kann und die Pods automatisch neu gestartet werden, wenn sie ausfallen.

### 6.5 Zusammenfassung

Durch den Einsatz von Kubernetes in Kombination mit einer kontinuierlichen Deployment-Pipeline wird sichergestellt, dass die Gardening App jederzeit skalierbar, hochverfügbar und robust bereitgestellt werden kann. Die Architektur ermöglicht eine klare Trennung der Verantwortlichkeiten zwischen dem Frontend, Backend und Data-Tier, wobei die Kommunikation über Kubernetes-Services und Ingress-Routen gesteuert wird.

## 7. Abdeckung der Anforderungen
| Anforderung | Umsetzung                                                                                                                                                                                                                                                    | Begründung |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|
| AF-1: DevOps / Continuous Deployment | Kubernetes Deployment                                                                                                                                                                                                                                        | Skalierbares und automatisiertes Deployment durch Kubernetes. |
| AF-2: Balance zwischen technischer Komplexität und Nutzungsfreude | Minimale Anzahl an Bedienelementen, keine Notwendigkeit für den Nutzer sich mit Berechnung des Suitability Score auseinanderzusetzen, graphische Untermalung der Wetterdaten, Prompt Engineering für für Laien verständlichen freundlich-witzigen Assistenten|
| AF-3: WebUI == Streamlit | Nutzung von Streamlit                                                                                                                                                                                                                                        | Streamlit bietet eine einfache Möglichkeit, interaktive WebUIs zu erstellen. |
| AF-4: LLMs und Backend-Services | LLM-Nutzung im Frontend                                                                                                                                                                                                                                      | Direkte Interaktion mit den Benutzern, um personalisierte Berichte zu erstellen. |
| AF-5: Intuitive Bedienbarkeit | Einfaches, klares UI                                                                                                                                                                                                                                         | Die App ist intuitiv und ohne lange Einarbeitungszeit bedienbar. |
| AF-6: Stateful Backend (Optional) | Verwendung von PostgreSQL                                                                                                                                                                                                                                    | Speicherung der relevanten Pflanzendaten in einer PostgreSQL-Datenbank. |
| AF-7: Wiederverwenden von Grafiken oder anderen gestaltenden Elementen | Nutzung von CC-lizenzierten Bildern                                                                                                                                                                                                                          | Einhaltung von Lizenzanforderungen bei der Nutzung von Grafiken. |
| AF-8: Dokumentation | Umfassende README.md und GitLab Wiki                                                                                                                                                                                                                         | Vollständige Dokumentation der Architektur und Funktionen der App. |

## 8. Quellen
- [EcoCrop Readme](https://github.com/OpenCLIM/ecocrop)
