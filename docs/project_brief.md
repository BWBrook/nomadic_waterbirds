# Project brief

## Working title: Hydrological reaction norms of Australia’s nomadic waterbirds.

Central aim: Estimate how Australian waterbird species and functional groups respond to changing wetland inundation through time, and identify which wetlands function as drought refugia, flood-pulse foraging sites, breeding-support wetlands, stepping-stones, or weakly used “false refugia”.

The project should not be framed as a generic SDM exercise. The ecological object is the reaction norm: the response of a species or guild to current and lagged hydrological states. A wetland’s value is not only its area, location or vegetation type; it is its recent hydrological history, its persistence, its novelty after drought, and its context within a broader landscape of scarce or abundant water. That is the conceptual hook.

## Scope

I would start with eastern and inland Australia rather than promising the whole continent on day one. The first operational scope should include the Murray–Darling Basin, Lake Eyre/Kati Thanda-connected systems where feasible, major eastern wetlands, and coastal drought-refuge systems. National expansion is allowed only if the data pass quality-control and validation gates. This keeps the project ambitious without letting it dissolve into a continental atlas.

The target taxa should be 30–60 waterbird species grouped into interpretable guilds: ducks and grebes, cormorants/darters, herons/egrets, ibis/spoonbills, pelicans, rails/coots, and perhaps a separate shorebird module if tidal and coastal detection issues can be handled. Colonial breeders should be treated separately because breeding requires persistence and nesting conditions, not just water presence.

## Core hypotheses

The first hypothesis is that species differ in hydrological lag structure. Opportunistic foragers such as some ducks, ibis and spoonbills should respond rapidly to newly inundated wetlands, whereas colonial breeders should require longer hydroperiod persistence before breeding or abundance peaks.

The second hypothesis is that hydrological novelty matters more than absolute water area for nomadic species. A newly wet basin after a dry spell may be more attractive than a permanently wet site of similar area, because flood pulses mobilise food resources.

The third hypothesis is that wetland value is context-dependent. A wetland that holds water during regional drought may function as a refuge, while the same wetland during region-wide flooding may be less important because birds are dispersed across many alternatives.

The fourth hypothesis is that drought refugia and breeding engines are not the same objects. Permanent coastal or regulated wetlands may hold birds through dry periods but contribute less to recruitment than large inland flood-pulse wetlands with sufficient hydroperiod persistence.

The fifth hypothesis is that species’ hydrological response traits can be partially predicted from functional guild, breeding strategy, dispersal ecology and conservation status. This gives the paper a comparative-ecology dimension rather than a species-by-species catalogue.

## Data plan

The hydrological layer should be built from DEA Water Observations, extracting monthly or seasonal water metrics for defined wetland units or grid cells: current wet area, proportion wet, recent change in wet area, wetting novelty after dry periods, cumulative wet months, drying velocity, and local hydroperiod persistence. Regional water availability should be calculated within biologically meaningful buffers, probably at multiple scales such as 50, 100 and 250 km, to capture landscape context. DEA explicitly supports analyses of wetland dynamics, drought, flooding and seasonal water patterns, which makes it the natural remote-sensing base.  ￼

The biodiversity layer should use eBird complete checklists as the main citizen-science stream, because complete lists allow stronger inference about non-detections than opportunistic presences. Birdata should be included if access and licensing allow, especially 2-ha 20-minute surveys because they are standardised and directly relevant to Australian bird monitoring. ALA records should be treated cautiously: useful for taxonomy, historical range context and rare-species presence, but not as the main source of absences or trends unless metadata support that use. The Eastern Australian Waterbird Survey should be used as either an independent validation stream or, if technically feasible, part of an integrated model with a separate observation process.  ￼

The project should also ingest rainfall, temperature and drought indices from public climate products, plus static wetland covariates such as wetland type, protected-area status, distance to coast, basin identity, elevation and surrounding land use. These should not become the centre of the project; they are explanatory context for hydrological response.

## Analytical design

The modelling should be hierarchical and explicitly observation-aware. At minimum, the citizen-science model should include effort covariates such as duration, distance, number of observers, protocol, time of day, day of year, checklist completeness, and spatial sampling intensity. Counts should be modelled as overdispersed and probably zero-inflated or hurdle-structured; occurrence can be modelled as a parallel or simpler endpoint. The key is not to pretend that citizen-science counts are aerial-survey abundance estimates.

The ecological process model should estimate species-specific and guild-level responses to hydrological covariates. These responses should be allowed to be nonlinear and lagged. A practical implementation would use hierarchical GAMMs, Bayesian additive models, INLA, Stan/TMB, or a two-stage machine-learning-plus-inference design, but the model class should be chosen for interpretability, not leaderboard prediction. The final paper needs legible reaction curves, not a black-box map.

A strong design would include three linked response layers: occurrence probability from complete checklists; relative abundance from checklist counts; and breeding or nesting evidence where aerial-survey data permit. The paper can still succeed with occurrence and relative abundance only, but breeding response would make it substantially stronger.

Validation must be non-negotiable. The model should be tested with spatial blocking, temporal blocking, and hydrological-event blocking. It should be asked to predict held-out wet years, dry years, flood-pulse years and wetland regions not used in training. The aerial-survey data should be used to test whether citizen-science-derived hydrological response patterns recover independent wetland-use patterns. Recent EAWS reports emphasise that wetland habitat remains a major driver of waterbird abundance, breeding and diversity, but that long-term declines and changing wetland availability complicate interpretation; this makes validation against the aerial-survey record especially valuable.  ￼

I would also include a synthetic-bias stress test. Simulate observer behaviour concentrated near roads, towns, popular wetlands and charismatic species, then test whether the model falsely infers hydrological responses under biased sampling. This does not need to dominate the paper, but it will inoculate the analysis against a predictable reviewer critique.

## Main outputs

The first scientific output should be a set of hydrological reaction norms for major waterbird guilds and selected species. These would show, for example, whether a species responds most strongly to current inundation, one-season lagged inundation, hydroperiod persistence, drying rate, or regional scarcity.

The second output should be a classification of wetlands by ecological role. I would use categories such as drought refuge, flood-pulse foraging wetland, breeding-support wetland, stepping-stone, variable-use wetland, and low-response/uncertain wetland. This classification must include uncertainty; a map without uncertainty would be weaker scientifically and potentially misleading for management.

The third output should be a hindcast of major hydrological episodes: severe drought, post-drought floods, La Niña flood years, and recent drying. This is where the paper becomes vivid. The model should show not only where water was, but which wetlands became biologically consequential for which species or guilds.

The fourth output should be a reproducible public workflow: code, data dictionaries, covariate extraction scripts, model specifications, validation reports and a clear licence/attribution statement. Derived data should be shared where allowed; otherwise, the workflow should be fully reproducible from the relevant requested datasets.

## Definition of done

The project is done when there is a submission-ready manuscript and a defensible reproducible repository that can survive hostile review. More concretely, done means: a pre-registered or internally frozen analysis plan; a documented species list and taxonomy concordance; a data-inclusion decision table explaining why each data stream was included, excluded or used only for validation; a wetland-unit layer with extracted hydrological time series; a fitted hierarchical model with interpretable species and guild response functions; blocked validation results; a bias-simulation sensitivity analysis; and a small number of polished figures that carry the argument without requiring the reader to trust hidden machinery.

The manuscript should be built around four main figures. Figure 1 should be the conceptual model: pulsed water, lagged bird response, regional scarcity, refuge versus breeding role. Figure 2 should show hydrological reaction norms for representative species and guilds. Figure 3 should map wetland ecological-role classes with uncertainty. Figure 4 should show hindcast redistribution during contrasting hydrological years. Supplementary material can carry the species-by-species detail. 

Note that the mansucript will be built using the templates and tooling available here: `/Users/bwbrook/work/makedoc`

## What you should be free to change

You should not be forced to keep a national scope if the validation shows that eastern Australia or the MDB-plus-arid-inland frame is more defensible. You are also free to drop Birdata if access or licensing becomes limiting, or to use it only as validation rather than as a primary model stream. You are free to choose the modelling engine, provided it produces interpretable hydrological response functions and passes blocked validation. The vision is the hydrological reaction-norm framework, not allegiance to a particular package, species count or map extent.

## What I would not compromise on (Lab Leader's caution)

I would not let this become a static SDM paper. I would not let opportunistic ALA records be treated as absences. I would not allow random cross-validation as the main evidence of predictive performance. I would not bury detectability and observer effort in a vague caveat. I would not present wetland maps without uncertainty. And I would not oversell causal inference: this is an observational synthesis of hydrological association, temporal response and predictive structure, not an experiment in which water was randomly assigned.

## Likely journal positioning

The natural homes would be a discipline-specific Q1-style ecology or conservation journal such as Journal of Applied Ecology, Global Change Biology, Diversity and Distributions, Global Ecology and Biogeography, Ecological Applications, or Methods in Ecology and Evolution if the observation-model/bias-integration component becomes the dominant contribution. My instinct is that the best version is not a methods paper. It should be sold as ecological synthesis: Australia’s nomadic waterbirds as a test case for how mobile communities track pulsed, climate-sensitive resources across continental wetland networks.

The concise pitch is this: Australia has the birds, the hydrological volatility, the conservation need, and now the public data infrastructure to quantify not just where waterbirds occur, but how they respond to water through time. That is a publishable ecological problem, and it is sharper than another atlas, another SDM, or another post-fire opportunistic-data analysis.

## Final notes

The core question is simple but strong: when water appears, persists, contracts or disappears across Australian wetlands, which waterbirds respond, how fast, in what numbers, and under what broader hydrological context? The intellectual appeal is that Australian waterbirds are almost custom-built for a pulsed-resource ecology project: they are mobile, often nomadic, strongly coupled to hydrological extremes, conservation-relevant, and supported by unusually good public or request-access datasets. The project also has a natural Q1-journal pitch because it bridges community ecology, movement/nomadism, climate-extreme ecology, citizen-science inference, remote sensing and wetland management.

I would not claim that a quick literature search proves absolute novelty, but I found no obvious exact duplicate. The closest existing work is strong but not the same project: long-term aerial surveys have already shown major waterbird declines and climate/water-management vulnerability in the Murray–Darling Basin and related systems; dynamic habitat modelling has been done for a small number of water-dependent species in the MDB; and there are high-quality annual aerial-survey datasets for eastern Australia and the MDB. The gap is a broader, multi-species, temporally explicit, detection-aware analysis of hydrological response functions across many waterbird species and wetland types, integrating satellite water dynamics with citizen-science and aerial-survey observations rather than treating wetlands as static habitat.

The data backbone is unusually favourable. DEA Water Observations provides long time-series information on wet/dry surface-water states from Landsat and Sentinel imagery, with coverage back to 1986 and summaries useful for wetland, drought and seasonal analyses. eBird’s Basic Dataset is available by request and updated monthly, while the ALA provides a national biodiversity-data infrastructure with large-scale occurrence access. Birdata adds standardised Australian bird-survey protocols, including the BirdLife/eBird 2-ha 20-minute survey collaboration, and the Eastern Australian Waterbird Survey has monitored continental-scale waterbird abundance, breeding and wetland extent since 1983.
