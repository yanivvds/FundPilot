# Teleknowledge Connect — Domeinkennis

Dit document beschrijft de domeinkennis die nodig is om de Teleknowledge Connect
databases effectief te bevragen met natuurlijke taal.

---

## Overzicht

Teleknowledge Connect is een contactcenterplatform dat wordt gebruikt voor fondsenwerving,
donateurbeheer en campagnemanagement. Het systeem beheert het complete proces van
outbound bellen tot donateurretentie.

---

## Database Architectuur

### CWESystemConfig
De **configuratiedatabase**. Bevat alle instellingen en structurele definities:

- **Projecten**: Elke opdrachtgever/goede doel heeft een of meerdere projecten.
  Een project definieert de campagne-instellingen, belregels en doelgroepen.
- **Werkgroepen**: Teams van agenten die belwerk uitvoeren. Een werkgroep is
  gekoppeld aan een of meerdere projecten.
- **Gebruikers**: Alle medewerkers/agenten in het systeem met hun rechten en rollen.
- **Resultaatcodes**: De mogelijke uitkomsten van een gesprek (bijv. "toezegging",
  "weigering", "terugbellen", "niet bereikt"). Cruciaal voor kwaliteitsanalyse.
- **Verbindingen**: Telefoonlijnen en SIP-trunks configuratie.
- **Systeeminstellingen**: Globale configuratieparameters.

### CWESystemData
De **operationele database**. Bevat alle runtime/productiedata:

- **Belgeschiedenis**: Elk telefoongesprek met starttijd, eindtijd, duur,
  resultaatcode, agent, project en werkgroep.
- **AI-uitkomsten**: Resultaten van AI-modellen die tijdens gesprekken worden ingezet.
- **Agentactiviteit**: Login/logout tijden, pauzes, statussen (beschikbaar, nabellen, pauze).
- **Gewerkte uren**: Urenregistratie per agent per dag.
- **ACD-data**: Automatic Call Distribution — hoe gesprekken worden verdeeld
  over agenten en wachtrijen.
- **Prestatie-indicatoren**: Operationele KPI's zoals gemiddelde gespreksduur,
  wachttijd, percentage bereikt.

### CWEProjectData
De **klantdatabase**. Bevat alle klant- en campagnespecifieke data:

- **Donordata**: Persoonsgegevens van donateurs (versleuteld waar nodig).
  Bevat adres, contactgegevens, donatiehistorie.
- **Klantrecords**: Leadlijsten en bellijsten per campagne.
- **Campagneresultaten**: Uitkomsten per campagne: conversie, omzet, kosten.
- **Projectresultaten**: Geaggregeerde resultaten per project.
- **Acquisitiedata**: Data over nieuwe donateurs: bron, kanaal, datum, eerste donatie.
- **Chargebacks**: Terugboekingen en geweigerde incasso's.
- **Toestemmingen**: GDPR/AVG-gerelateerde toestemmingsregistraties.

### Archiefdatabases
Elke primaire database heeft een `_Archive` variant:
- `CWESystemConfig_Archive`
- `CWESystemData_Archive`
- `CWEProjectData_Archive`

Data wordt periodiek verplaatst naar het archief maar behoudt dezelfde tabelstructuur.
Archiefdata is essentieel voor:
- Trendanalyse over langere perioden
- Retentieberekeningen
- Lifetime Value bepaling
- Seizoenspatronen
- Historische vergelijkingen

---

## Veelgebruikte Analyse Patronen

### 1. Herkomst Beste Donateurs
**Databases**: CWEProjectData + CWESystemConfig
**Aanpak**: Join projectgegevens met campagne-instellingen.
Groepeer op kanaal, leverancier, regio. Bereken niet alleen volume maar ook
gemiddelde donatiewaarde en behoud na 12 maanden.

### 2. Retentie-analyse
**Databases**: CWEProjectData + CWEProjectData_Archive
**Aanpak**: Bepaal per cohort (instroommand) hoeveel donateurs nog actief zijn
na 1, 3, 6 en 12 maanden. Vergelijk per kanaal en leverancier.
Gebruik UNION ALL om actuele en archiefdata te combineren.

### 3. Kostprijs per Duurzame Donateur
**Databases**: CWEProjectData + CWESystemData
**Aanpak**: Tel de totale kosten (belminuten × tarief + overhead) en deel door
het aantal donateurs dat na 6 maanden nog actief is. Trek chargebacks af.

### 4. Campagne-effectiviteit
**Databases**: CWEProjectData + CWESystemConfig + CWESystemData
**Aanpak**: Vergelijk campagnes op conversiepercentage, gemiddelde donatiewaarde,
kosten per acquisitie. Kijk naar timing (dag van de week, tijdstip) en seizoen.

### 5. Verborgen Verliezen
**Databases**: CWEProjectData + CWESystemData
**Aanpak**: Identificeer regio's of leveranciers waar de churn bovengemiddeld is.
Bereken netto-opbrengst na aftrek van chargebacks en vroege uitval.

### 6. Donateur-profiel
**Databases**: CWEProjectData + CWESystemData
**Aanpak**: Analyseer gedragspatronen (niet persoonskenmerken) van donateurs
die >12 maanden actief blijven vs. die binnen 3 maanden afhaken.

### 7. Campagne-interventies
**Databases**: CWESystemData (real-time) + CWEProjectData
**Aanpak**: Monitor lopende campagnes op conversie per uur/dag. Vergelijk met
historische baseline. Signaleer afwijkingen.

### 8. Marktpositie
**Databases**: Alle + Archive
**Aanpak**: Vergelijk huidige KPI's (CPA, retentie, conversie) met historische
gemiddelden. Bereken trends over kwartalen.

### 9. Compliance
**Databases**: CWEProjectData
**Aanpak**: Check percentage records met volledige toestemming. Identificeer
fouten per kanaal. Tel klachten en opt-outs.

### 10. Groeikansen
**Databases**: CWEProjectData + CWESystemConfig + Archive
**Aanpak**: Rangschik kanalen/leveranciers op netto-opbrengst per donateur.
Identificeer welke combinaties nog niet op volume draaien maar wel hoge kwaliteit leveren.

---

## Veelvoorkomende SQL Patronen

### Cross-database JOIN
```sql
SELECT c.ProjectName, d.DonorCount
FROM [CWESystemConfig].[dbo].[Projects] c
JOIN (
    SELECT ProjectID, COUNT(*) AS DonorCount
    FROM [CWEProjectData].[dbo].[Donors]
    GROUP BY ProjectID
) d ON c.ProjectID = d.ProjectID
```

### Actueel + Archief combineren
```sql
SELECT * FROM [CWESystemData].[dbo].[CallHistory]
WHERE CallDate >= '2025-01-01'
UNION ALL
SELECT * FROM [CWESystemData_Archive].[dbo].[CallHistory]
WHERE CallDate >= '2025-01-01'
```

### Retentie per cohort
```sql
WITH Cohort AS (
    SELECT DonorID, MIN(DonationDate) AS FirstDonation
    FROM [CWEProjectData].[dbo].[Donations]
    GROUP BY DonorID
)
SELECT 
    FORMAT(c.FirstDonation, 'yyyy-MM') AS Cohort,
    COUNT(DISTINCT c.DonorID) AS TotaalDonateurs,
    COUNT(DISTINCT CASE 
        WHEN d.DonationDate >= DATEADD(MONTH, 6, c.FirstDonation) 
        THEN d.DonorID 
    END) AS ActiefNa6Maanden
FROM Cohort c
LEFT JOIN [CWEProjectData].[dbo].[Donations] d ON c.DonorID = d.DonorID
GROUP BY FORMAT(c.FirstDonation, 'yyyy-MM')
ORDER BY Cohort
```

---

## Belangrijke Begrippen

| Nederlands | Engels | Betekenis |
|-----------|--------|-----------|
| Donateur | Donor | Persoon die doneert aan een goed doel |
| Toezegging | Pledge | Belofte tot donatie tijdens telefoongesprek |
| Bevestiging | Confirmation | Schriftelijke bevestiging van toezegging |
| Chargeback | Chargeback | Terugboeking van een incasso door de bank |
| Retentie | Retention | Percentage donateurs dat actief blijft |
| Uitval | Churn | Verlies van donateurs |
| CPA | Cost Per Acquisition | Kosten per geworven donateur |
| LTV | Lifetime Value | Totale waarde van een donateur over tijd |
| ACD | Automatic Call Distribution | Automatische gespreksverdeling |
| Werkgroep | Workgroup | Team van agenten |
| Resultaatcode | Result Code | Uitkomst van een gesprek |
| Belpoging | Call Attempt | Een poging om iemand te bereiken |
| Bereikt | Reached | Succesvol contact gehad |
| Nabellen | After-call work | Administratie na een gesprek |
| Wraptime | Wrap time | Tijd besteed aan nabellen |
