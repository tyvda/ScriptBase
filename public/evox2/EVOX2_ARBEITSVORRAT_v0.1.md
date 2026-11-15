# EVOX2 – Arbeitsvorrat (Backlog)

**Version:** 0.1  
**Stand:** 2026-11-14  
**Produktverantwortung und Freigabe:** Betreiber (`sebastian`)  
**Ausführender Entwicklungsassistent:** die **eine** bestehende OpenClaw-Instanz mit lokalem Ollama und Telegram  
**Projektablage auf dem Host:** `~/.openclaw/workspace/evox2-dev`  
**Projektablage in der Docker-Sandbox:** `/mnt/evox2-dev`

## 0. Zweck und Evidenzgrenzen

Dieser Arbeitsvorrat steuert den **schrittweisen Wiederaufbau von EVOX2**, während die bestehende OpenClaw-Instanz weiterläuft. Die neue Architektur wird getrennt entworfen und getestet; ein späterer Wechsel ist eine eigenständige, menschlich freizugebende Entscheidung. Das alte Backup und `/srv/ai` sind **keine** automatisch aktivierte Laufzeit.

Die Aufgaben beruhen auf (a) den bisher vom Betreiber geposteten Host- und Telegram-Ergebnissen und (b) historischen EVOX2-Unterlagen vom 7./10. November 2026. **Historische Tests, Versionen, Installationen oder Reviews sind keine aktuelle Zielmaschinenabnahme.** Der genaue Inhalt der auf dem Host neu erzeugten EP-1B/C/D-Berichte wurde in dieser Fassung nicht unabhängig gelesen; ihr Status wird daher als *vom Bot gemeldet* bezeichnet.

## 1. Verbindliche Arbeitsregeln

1. **Ein Arbeitsauftrag zurzeit.** Der Agent darf genau eine explizit freigegebene Backlog-ID ausführen. Andere Aufgaben bleiben unangetastet.
2. **Backlog ≠ Ausführungsfreigabe.** `bereit` und `geplant` berechtigen weder zu Dateiänderungen noch zu Installation, Tests, Commits oder Dienststarts. Jede Ausführung benötigt eine gesonderte Freigabe mit ID und Umfang.
3. **Keine stillen Folgeaufträge.** Nach jeder Aufgabe Ergebnisbericht und Stopp; keine automatische Aufnahme des nächsten Tasks, keine selbstständige Umschaltung.
4. **Keine eigenmächtigen Git-Commits, Tags, Remotes oder Pushes.** Änderungen zunächst im Working Tree dokumentieren; gesonderte Freigabe vor einem Commit. Vor Arbeiten Git-Status und bestehende Änderungen prüfen.
5. **Sandbox beibehalten:** Rootless Docker, `network=none`, `readOnlyRootfs=true`, `capDrop=ALL`, `no-new-privileges`; kein Docker-Socket, keine Host-Shell, keine zusätzlichen Mounts oder Elevated Tools für Agenten.
6. **Host-Inventare über den Betreiber:** Der Betreiber erstellt und prüft lesende Snapshots auf Ubuntu; der Agent analysiert nur gezielt bereitgestellte Dateien. Keine Zugriffs-/ACL-Änderungen an `/srv/ai`, keine historischen Runner ohne gesonderte Freigabe ausführen.
7. **Fail-closed:** `HOLD` für produktiven Dispatch, Ghost `approved_inactive`, kein Deployment/Publisher/GitHub-Push; weder Telegram-Nachrichten noch LLM-Aussagen gelten als technische Autorisierung.
8. **Nachweise je Aufgabe:** Quelle/Dateipfad, beobachtetes Resultat, Testmethode, verbleibende Unsicherheit, Änderungen und gegebenenfalls Git-Diff angeben; Telegram-Bericht kurz halten.
9. **Keine ungeprüfte Ausführung:** Historische Skripte, TAR-Archive, SQL-Dateien und wiederhergestellte Konfigurationen sind zunächst nicht vertrauenswürdige Referenzartefakte.

### Statuswerte

`GEPLANT` = auf dem Arbeitsvorrat, nicht freigegeben; `BEREIT` = fachlich vorbereitet, **nicht** freigegeben; `FREIGEGEBEN` = für genau definierten Umfang ausdrücklich vom Betreiber genehmigt; `IN_ARBEIT` = genehmigt und begonnen; `PRUEFUNG` = Ergebnis liegt vor, Abnahme offen; `ABGENOMMEN` = Betreiber hat konkrete Ergebnisse akzeptiert; `BLOCKIERT` = fehlt Voraussetzung; `ZURUECKGESTELLT` = bewusst nicht jetzt.

**WIP-Grenze:** maximal eine ID mit `FREIGEGEBEN` oder `IN_ARBEIT`. Der Agent darf Status `ABGENOMMEN` nicht eigenständig setzen.

## 2. Referenzstatus vor Beginn dieses Backlogs

| Arbeitsphase | Berichteter Stand | Einordnung |
|---|---|---|
| EP-0 Bootstrap | Git-Repository und Tag `v0.0.0-bootstrap`, Commit `4d2bd9a` | vom Betreiber auf Host geprüft |
| EP-1A Quellen | fünf Dokumente verifiziert, zwei Inventarberichte | vom Bot abgeschlossen gemeldet |
| EP-1B Ist/Soll | drei Berichte, Commit `53c4b4c` | gemeldet; frühe historische Ist-Aussagen waren zu korrigieren |
| EP-1C Hostabgleich | Host-Nachweise; später CPU-/RAM-Korrektur, Bericht teilweise belegt | teilweiser Nachweis; Stage-Runner/DB offen; Commits `691f7e5`, `508cf2b` berichtet |
| EP-1D Historische Artefakte | drei Inventarberichte erstellt, keine Installation | **Inventar gemeldet; inhaltliche Abnahme und Korrekturen offen** |
| Gegenwärtige OpenClaw-Laufzeit | OpenClaw `2026.11.3`, Telegram verbunden, Ollama `0.40.16`, Rootless Docker `29.9.3` | gemäß Betreiber-Hostausgaben |
| PostgreSQL / Stage 17/18 | PostgreSQL nicht als aktiver Hostdienst nachgewiesen; frühere Stage-Artefakte nur begrenzt zugänglich | keine Wiederherstellungs-/Produktionsabnahme |

## 3. Priorisierter Arbeitsvorrat

**P0** = zuerst für sichere Rekonstruktion; **P1** = nächster Entwicklungsblock nach Grundlagen; **P2** = später vor Freigabe/Cutover. Die Reihenfolge ist eine Planungsempfehlung, keine automatische Ausführungsreihenfolge.

| ID | Prio | Status | Thema | Abhängigkeit | Abnahmekriterium |
|---|---|---|---|---|---|
| **EVX-001** | P0 | BEREIT | **EP-1D fachlich korrigieren und abnehmen**: PG-Zielversion 18, „nicht nachgewiesen“ ≠ „nirgendwo vorhanden“, 11 Blocker + 1 Medium laut gemeldeter Liste, keine Pauschal-ACLs | Drei EP-1D-Berichte | Aussagen mit Fundstellen korrigiert; keine Installations- oder Rechtemanipulation; Betreiber prüft |
| **EVX-002** | P0 | GEPLANT | **Git-/Freigabe-Audit**: Arbeitsbaum, Commit-Historie, unautorisierte Commits und offene Diffs erfassen (ohne Reset) | EP-1D-Ergebnis | Lesendes Protokoll mit betroffenen Dateien/Commits, keine weiteren Commits |
| **EVX-003** | P0 | GEPLANT | **Evidenzregister**: aktuell / historisch / unbekannt; Verweis auf Host-Snapshot, Quellhashes und genaue Belegstelle | EP-1A–D | Für jede zentrale Aussage klare Quelle, Zeitpunkt und Nachweisklasse |
| **EVX-004** | P0 | GEPLANT | **Backup-/Quellenkatalog planen**: vorliegende Chat-Uploads, `/srv/ai` und andere noch nicht restaurierte Backups getrennt kennzeichnen | EVX-003 | Manifestvorschlag und ungefährlicher Übernahmepfad; nichts ausführen/entpacken |
| **EVX-005** | P0 | GEPLANT | **PostgreSQL-18-Wiederherstellungsanalyse**: verfügbare SQL-Dateien, Cluster-/Backup-Spuren und Kompatibilität inventarisieren | EVX-004 | Nachweis-/Lückenliste; kein Clusterstart, kein SQL-Import |
| **EVX-006** | P0 | GEPLANT | **Stage-17/18-Artefakt-Provenienz**: historische TAR-/SQL-/Runner-Stände vergleichen, Rechte- und Zugriffsgrenzen dokumentieren | EVX-004 | Dateiliste + Hashes + Unbekanntes; keine Skriptausführung und kein pauschales `chmod/chown` |
| **EVX-007** | P0 | GEPLANT | **EP-2A Architektur-/Migrationsplan** mit **einer** OpenClaw-Instanz und getrennter Entwicklungs-/späterer Laufzeit | EVX-003, EVX-005, EVX-006 | Versionierter Sollplan, Zuständigkeiten, Abhängigkeiten, Freigabegrenzen, Rückfallweg |
| **EVX-008** | P0 | GEPLANT | **Sicherheits- und Freigabematrix**: B1–B6, fünf offene M1-Befunde, M2/Stage-18-Reviewgrenzen, reale Owner | EVX-007 | Explizites `HOLD` bei fehlender unabhängiger Evidenz; keine Freigabe allein aus Offline-Tests |
| **EVX-009** | P0 | GEPLANT | **Backup-/Restore-Testkonzept** vor produktiven Datenänderungen | EVX-007 | RPO/RTO, Kopien, Testwiederherstellung und Stop-/Rollbackkriterien dokumentiert |
| **EVX-010** | P1 | GEPLANT | **Isolierten PostgreSQL-18-Testaufbau spezifizieren** | EVX-005, EVX-007, EVX-009 | Minimale DB-Scope/Isolation, Rollen, Restore- und Abschaltplan zur Betreiberfreigabe |
| **EVX-011** | P1 | GEPLANT | **Schema-/Rollenmatrix offline prüfen**, keine produktive Migration | EVX-010, EVX-006 | Schema-, Rollen-, Grant- und Migrations-Diff plus Negativtestplan |
| **EVX-012** | P1 | GEPLANT | **Stage-17-Testkette isoliert reproduzieren**, mit überprüfter Artefaktherkunft | EVX-006, EVX-010 | Runner- und Testprotokoll samt Abweichungen, keine Produktionsfreigabe |
| **EVX-013** | P1 | GEPLANT | **Stage-18-M2.x-Verifikation in separatem Testmodus**, zunächst ohne Reviewer-Install | EVX-012, EVX-008 | Wiederholbare Offline-Tests, Befunde getrennt von unabhängiger Abnahme |
| **EVX-014** | P1 | GEPLANT | **Minimalen Trusted-Workflow-Vertrag** (Job, Attempt, Fencing, Freigaben, Ergebnisstatus) entwerfen/implementieren | EVX-007, EVX-011 | Isolierte Testfälle, Autorisierung fail-closed, kein produktiver Dispatch |
| **EVX-015** | P1 | GEPLANT | **Eine OpenClaw-Instanz als zukünftige Systemkomponente anbinden**, erst als begrenzten Testadapter | EVX-014 | Testpfad mit klaren Prozess-, Daten- und Rückfallgrenzen; kein zweiter Gateway |
| **EVX-016** | P1 | GEPLANT | **Telegram-Statuskanal für EVOX2**, zuerst nur lesende Statusabfragen | EVX-014, EVX-008 | Bot bleibt verbunden; keine Telegram-Nachricht kann Jobs autorisieren/produktiv starten |
| **EVX-017** | P2 | ZURUECKGESTELLT | **Unabhängiger Reviewer, Provenienz und Signaturverwahrung** | EVX-008, EVX-013 | Extern bestätigte Belege/Schlüsselverwahrung; keine scheinbare Unabhängigkeit durch lokale UID |
| **EVX-018** | P2 | ZURUECKGESTELLT | **Cutover-/Rollback-Generalprobe** und ausdrückliches Go/No-Go | EVX-009, EVX-014–017 | Unabhängige Abnahme, B1–B6 geschlossen, M1-Befunde geprüft, Betreiber-Go; sonst `HOLD` |

## 4. Nächster konkret vorbereiteter Auftrag

**Kandidat:** `EVX-001`. Dieser Eintrag ist **BEREIT, aber noch nicht freigegeben**.

**Umfang:** Nur die bestehenden drei EP-1D-Berichte lesen und befundbezogen korrigieren. Das PostgreSQL-18-Ziel, Unsicherheiten bei nicht zugänglichen Backupdaten, die korrekte Klassifizierung der offenen Befunde und das Verbot pauschaler Rechteänderungen herausarbeiten.

**Erlaubte Ausgaben:** Änderungen an diesen Berichten und eine kurze Telegram-Zusammenfassung. **Nicht erlaubt:** Installationen, Deployments, Hostbefehle, Bearbeiten anderer Dateien, automatische Commits/Tags, Rechteänderungen, neue EPs.

**Definition of Done:** `git diff --check` erfolgreich; geänderte Abschnitte benannt; keine unzulässigen Aktionen; Betreiber hat die Änderungen gesehen und EP-1D-inhaltliche Abnahme gesondert entschieden.

## 5. Standard-Vorlage für neue Aufgaben

```markdown
### EVX-XXX – <Titel>
- Priorität: P0 / P1 / P2
- Status: GEPLANT
- Ausgangspunkt / Quellen:
- Ziel und Nicht-Ziele:
- Voraussetzungen:
- Zulässige Dateien und Werkzeuge:
- Arbeitsschritte (max. 5):
- Test-/Beleganforderungen:
- Stop-/Fehlerbedingungen:
- Definition of Done:
- Benötigte Freigabe durch Betreiber:
- Abschlussbeleg / Git-Diff:
```

## 6. Standard-Telegram-Abschlussformat

```text
EVX-XXX – STATUS: PRUEFUNG / BLOCKIERT
Umgesetzt: <max. 3 Sätze>
Dateien: <konkrete Pfade>
Geprüft: <Befehl/Test, Ergebnis>
Offen: <konkreter Befund>
Git: <dirty/clean, KEIN Commit ohne Freigabe>
Nächster sinnvoller Task: EVX-YYY (nur Vorschlag, nicht starten)
```

## 7. Pflege dieses Arbeitsvorrats

- Der Agent darf Fortschritte **vorschlagen**, nicht die Freigabestufe selbständig erhöhen.
- Statusänderungen mit Datum, tatsächlichem Nachweis und verantwortlicher Freigabe versehen.
- Nach jedem Task den Betreiber um Abnahme bitten; erst danach den nächsten Task vorschlagen.
- Nicht automatisch Git committen. Änderungen am Backlog und an Quelldateien sind selbst Arbeitsänderungen und benötigen einen entsprechend begrenzten Auftrag.
- **Nächste Aktion:** Arbeitsvorrat kontrolliert in `docs/ARBEITSVORRAT.md` übernehmen, danach `EVX-001` separat freigeben.