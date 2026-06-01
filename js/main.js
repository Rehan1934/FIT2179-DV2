const charts = [
  ["#vis1", "specs/01_kpi_cards.json"],
  ["#vis2", "specs/02_symptom_rates.json"],
  ["#vis3", "specs/03_symptom_overlap.json"],
  ["#vis4", "specs/04_treatment_gap.json"],
  ["#vis5", "specs/05_gender_symptoms.json"],
  ["#vis6", "specs/06_year_symptoms.json"],
  ["#vis7", "specs/07_cgpa_symptoms.json"],
  ["#vis8", "specs/08_malaysia_trend.json"],
  ["#vis9", "specs/09_asean_comparison.json"],
  ["#vis10", "specs/10_asean_map.json"],
  ["#vis11", "specs/11_adolescent_warning_signs.json"],
  ["#vis12", "specs/12_attempted_suicide_age_sex.json"],
  ["#vis13", "specs/13_pressure_profile.json"]
];

async function embedChart(selector, specUrl) {
  try {
    const response = await fetch(specUrl);

    if (!response.ok) {
      throw new Error(`Could not load ${specUrl}`);
    }

    const spec = await response.json();

    await vegaEmbed(selector, spec, {
      actions: false,
      renderer: "svg"
    });

  } catch (error) {
    console.error(error);

    const el = document.querySelector(selector);
    if (el) {
      el.innerHTML = `<p class="caption">Chart failed to load. Check the path: ${specUrl}</p>`;
    }
  }
}

charts.forEach(([selector, spec]) => embedChart(selector, spec));