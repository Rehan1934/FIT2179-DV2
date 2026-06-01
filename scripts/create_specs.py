from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[1]
SPEC_DIR = BASE_DIR / "specs"
SPEC_DIR.mkdir(parents=True, exist_ok=True)


def write_spec(filename, spec):
    path = SPEC_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    print(f"Saved {path.relative_to(BASE_DIR)}")


base_config = {
    "config": {
        "background": "transparent",
        "font": "Inter",
        "view": {"stroke": None},
        "axis": {
            "labelFont": "Inter",
            "titleFont": "Inter",
            "labelColor": "#52616b",
            "titleColor": "#132238",
            "gridColor": "#e8eef5",
            "domainColor": "#d6e0ea",
            "tickColor": "#d6e0ea"
        },
        "legend": {
            "labelFont": "Inter",
            "titleFont": "Inter",
            "labelColor": "#52616b",
            "titleColor": "#132238",
            "orient": "bottom"
        },
        "title": {
            "font": "Inter",
            "fontSize": 15,
            "fontWeight": 700,
            "color": "#132238",
            "anchor": "start"
        }
    }
}


def with_config(spec):
    spec.update(base_config)
    return spec


# 01 KPI CARDS
write_spec("01_kpi_cards.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "KPI card style view of depression, anxiety, panic attacks and treatment seeking.",
    "data": {"url": "data/processed/student_kpis.csv"},
    "transform": [
        {"calculate": "format(datum.value, '.1f') + '%'", "as": "value_label"},
        {"calculate": "datum.count + ' of ' + datum.total + ' students'", "as": "count_label"}
    ],
    "facet": {
        "field": "indicator",
        "type": "nominal",
        "columns": 4,
        "header": {
            "labelFont": "Inter",
            "labelFontSize": 13,
            "labelFontWeight": 700,
            "labelColor": "#132238",
            "labelLimit": 150,
            "title": None
        }
    },
    "spec": {
        "width": 165,
        "height": 100,
        "layer": [
            {
                "mark": {
                    "type": "text",
                    "font": "Inter",
                    "fontSize": 38,
                    "fontWeight": 800,
                    "dy": -6
                },
                "encoding": {
                    "x": {"value": 82},
                    "y": {"value": 42},
                    "text": {"field": "value_label"},
                    "color": {
                        "condition": {
                            "test": "datum.group === 'Support seeking'",
                            "value": "#65a891"
                        },
                        "value": "#7c6bb0"
                    },
                    "tooltip": [
                        {"field": "indicator", "type": "nominal"},
                        {"field": "value", "type": "quantitative", "title": "Percentage", "format": ".1f"},
                        {"field": "count", "type": "quantitative"},
                        {"field": "total", "type": "quantitative"}
                    ]
                }
            },
            {
                "mark": {
                    "type": "text",
                    "font": "Inter",
                    "fontSize": 12,
                    "color": "#52616b"
                },
                "encoding": {
                    "x": {"value": 82},
                    "y": {"value": 78},
                    "text": {"field": "count_label"}
                }
            }
        ]
    }
}))


# 02 SYMPTOM RATES
write_spec("02_symptom_rates.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Horizontal bar chart of student symptom rates.",
    "data": {"url": "data/processed/symptom_rates.csv"},
    "width": "container",
    "height": 230,
    "encoding": {
        "y": {
            "field": "indicator",
            "type": "nominal",
            "sort": "-x",
            "title": None
        },
        "x": {
            "field": "value",
            "type": "quantitative",
            "title": "Students reporting symptom (%)",
            "scale": {"domain": [0, 50]}
        },
        "color": {
            "field": "indicator",
            "type": "nominal",
            "legend": None,
            "scale": {
                "domain": ["Depression", "Anxiety", "Panic attacks"],
                "range": ["#7c6bb0", "#4f8fc0", "#e08e79"]
            }
        },
        "tooltip": [
            {"field": "indicator", "type": "nominal"},
            {"field": "value", "type": "quantitative", "title": "Percentage", "format": ".1f"},
            {"field": "count", "type": "quantitative"},
            {"field": "total", "type": "quantitative"}
        ]
    },
    "layer": [
        {
            "mark": {"type": "bar", "cornerRadiusEnd": 8}
        },
        {
            "mark": {
                "type": "text",
                "align": "left",
                "dx": 6,
                "fontSize": 12,
                "fontWeight": 700,
                "color": "#132238"
            },
            "encoding": {
                "text": {"field": "value", "type": "quantitative", "format": ".1f"}
            }
        }
    ]
}))


# 03 SYMPTOM OVERLAP
write_spec("03_symptom_overlap.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Bar chart showing number of symptoms reported by respondents.",
    "data": {"url": "data/processed/symptom_overlap.csv"},
    "width": "container",
    "height": 230,
    "encoding": {
        "x": {
            "field": "label",
            "type": "ordinal",
            "sort": ["No reported symptoms", "One symptom", "Two symptoms", "Three symptoms"],
            "title": "Number of reported symptoms"
        },
        "y": {
            "field": "percentage",
            "type": "quantitative",
            "title": "Students (%)",
            "scale": {"domain": [0, 50]}
        },
        "color": {
            "field": "symptom_count",
            "type": "ordinal",
            "legend": None,
            "scale": {
                "domain": [0, 1, 2, 3],
                "range": ["#d9e4ef", "#7fb3c8", "#7c6bb0", "#e08e79"]
            }
        },
        "tooltip": [
            {"field": "label", "type": "nominal"},
            {"field": "percentage", "type": "quantitative", "title": "Percentage", "format": ".1f"},
            {"field": "count", "type": "quantitative"}
        ]
    },
    "layer": [
        {"mark": {"type": "bar", "cornerRadiusEnd": 8}},
        {
            "mark": {
                "type": "text",
                "dy": -8,
                "fontSize": 12,
                "fontWeight": 700,
                "color": "#132238"
            },
            "encoding": {
                "text": {"field": "percentage", "type": "quantitative", "format": ".1f"}
            }
        }
    ]
}))


# 04 TREATMENT GAP
write_spec("04_treatment_gap.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Lollipop chart showing symptom and treatment gap.",
    "data": {"url": "data/processed/treatment_gap.csv"},
    "width": "container",
    "height": 260,
    "encoding": {
        "y": {
            "field": "indicator",
            "type": "nominal",
            "sort": "-x",
            "title": None,
            "axis": {"labelLimit": 280}
        },
        "x": {
            "field": "value",
            "type": "quantitative",
            "title": "Share of all student respondents (%)",
            "scale": {"domain": [0, 80]}
        },
        "color": {
            "field": "type",
            "type": "nominal",
            "scale": {
                "domain": ["warning sign", "support", "gap"],
                "range": ["#7c6bb0", "#65a891", "#e08e79"]
            },
            "title": "Category"
        },
        "tooltip": [
            {"field": "indicator", "type": "nominal"},
            {"field": "value", "type": "quantitative", "title": "Percentage", "format": ".1f"},
            {"field": "count", "type": "quantitative"},
            {"field": "total", "type": "quantitative"}
        ]
    },
    "layer": [
        {
            "mark": {"type": "rule", "strokeWidth": 4, "opacity": 0.35},
            "encoding": {
                "x": {"value": 0},
                "x2": {"field": "value"}
            }
        },
        {
            "mark": {"type": "circle", "size": 220, "opacity": 0.95}
        },
        {
            "mark": {
                "type": "text",
                "align": "left",
                "dx": 10,
                "fontSize": 12,
                "fontWeight": 700,
                "color": "#132238"
            },
            "encoding": {
                "text": {"field": "value", "type": "quantitative", "format": ".1f"}
            }
        }
    ]
}))


# 05 GENDER HEATMAP
write_spec("05_gender_symptoms.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Heatmap of symptoms by gender.",
    "data": {"url": "data/processed/gender_symptom_rates.csv"},
    "width": "container",
    "height": 220,
    "encoding": {
        "x": {"field": "symptom", "type": "nominal", "title": None},
        "y": {"field": "gender", "type": "nominal", "title": None},
        "color": {
            "field": "percentage",
            "type": "quantitative",
            "title": "%",
            "scale": {"scheme": "blues"}
        },
        "tooltip": [
            {"field": "gender", "type": "nominal"},
            {"field": "symptom", "type": "nominal"},
            {"field": "percentage", "type": "quantitative", "title": "Percentage", "format": ".1f"},
            {"field": "count", "type": "quantitative"},
            {"field": "group_total", "type": "quantitative", "title": "Group total"}
        ]
    },
    "layer": [
        {"mark": {"type": "rect", "cornerRadius": 6}},
        {
            "mark": {"type": "text", "fontSize": 12, "fontWeight": 700},
            "encoding": {
                "text": {"field": "percentage", "type": "quantitative", "format": ".1f"},
                "color": {
                    "condition": {"test": "datum.percentage > 45", "value": "white"},
                    "value": "#132238"
                }
            }
        }
    ]
}))


# 06 YEAR HEATMAP
write_spec("06_year_symptoms.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Heatmap of symptoms by year of study.",
    "data": {"url": "data/processed/year_symptom_rates.csv"},
    "width": "container",
    "height": 240,
    "encoding": {
        "x": {"field": "symptom", "type": "nominal", "title": None},
        "y": {
            "field": "year_of_study",
            "type": "ordinal",
            "sort": ["Year 1", "Year 2", "Year 3", "Year 4"],
            "title": None
        },
        "color": {
            "field": "percentage",
            "type": "quantitative",
            "title": "%",
            "scale": {"scheme": "purples"}
        },
        "tooltip": [
            {"field": "year_of_study", "type": "ordinal", "title": "Year"},
            {"field": "symptom", "type": "nominal"},
            {"field": "percentage", "type": "quantitative", "title": "Percentage", "format": ".1f"},
            {"field": "count", "type": "quantitative"},
            {"field": "group_total", "type": "quantitative", "title": "Group total"}
        ]
    },
    "layer": [
        {"mark": {"type": "rect", "cornerRadius": 6}},
        {
            "mark": {"type": "text", "fontSize": 12, "fontWeight": 700},
            "encoding": {
                "text": {"field": "percentage", "type": "quantitative", "format": ".1f"},
                "color": {
                    "condition": {"test": "datum.percentage > 45", "value": "white"},
                    "value": "#132238"
                }
            }
        }
    ]
}))


# 07 CGPA DOT PLOT
write_spec("07_cgpa_symptoms.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Dot plot of symptoms by CGPA range.",
    "data": {"url": "data/processed/cgpa_symptom_rates.csv"},
    "width": "container",
    "height": 260,
    "encoding": {
        "y": {
            "field": "cgpa",
            "type": "ordinal",
            "sort": ["0 - 1.99", "2.00 - 2.49", "2.50 - 2.99", "3.00 - 3.49", "3.50 - 4.00"],
            "title": "CGPA range"
        },
        "x": {
            "field": "any_symptom_percentage",
            "type": "quantitative",
            "title": "Students with at least one symptom (%)",
            "scale": {"domain": [0, 100]}
        },
        "size": {
            "field": "count",
            "type": "quantitative",
            "title": "Students in group",
            "scale": {"range": [80, 500]}
        },
        "color": {"value": "#7c6bb0"},
        "tooltip": [
            {"field": "cgpa", "type": "ordinal", "title": "CGPA"},
            {"field": "any_symptom_percentage", "type": "quantitative", "title": "Any symptom (%)", "format": ".1f"},
            {"field": "avg_symptom_count", "type": "quantitative", "title": "Average symptom count"},
            {"field": "count", "type": "quantitative", "title": "Students"}
        ]
    },
    "layer": [
        {
            "mark": {"type": "rule", "color": "#d9e4ef"},
            "encoding": {
                "x": {"value": 0},
                "x2": {"field": "any_symptom_percentage"}
            }
        },
        {"mark": {"type": "circle", "opacity": 0.9}},
        {
            "mark": {
                "type": "text",
                "align": "left",
                "dx": 12,
                "fontSize": 12,
                "fontWeight": 700,
                "color": "#132238"
            },
            "encoding": {
                "text": {"field": "any_symptom_percentage", "type": "quantitative", "format": ".1f"}
            }
        }
    ]
}))


# 08 MALAYSIA TREND
write_spec("08_malaysia_trend.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Malaysia depression and anxiety prevalence trend.",
    "data": {"url": "data/processed/malaysia_depression_anxiety_trend.csv"},
    "width": "container",
    "height": 310,
    "encoding": {
        "x": {
            "field": "year",
            "type": "temporal",
            "title": "Year",
            "axis": {"format": "%Y"}
        },
        "y": {
            "field": "prevalence",
            "type": "quantitative",
            "title": "Estimated prevalence (%)",
            "scale": {"zero": False}
        },
        "color": {
            "field": "disorder",
            "type": "nominal",
            "scale": {
                "domain": ["Depression", "Anxiety"],
                "range": ["#7c6bb0", "#4f8fc0"]
            },
            "title": "Condition"
        },
        "tooltip": [
            {"field": "year", "type": "temporal", "format": "%Y"},
            {"field": "disorder", "type": "nominal"},
            {"field": "prevalence", "type": "quantitative", "title": "Prevalence (%)", "format": ".2f"}
        ]
    },
    "layer": [
        {"mark": {"type": "line", "strokeWidth": 3}},
        {"mark": {"type": "point", "filled": True, "size": 45}}
    ]
}))


# 09 ASEAN COMPARISON
write_spec("09_asean_comparison.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "ASEAN depression prevalence comparison with Malaysia highlighted.",
    "data": {"url": "data/processed/asean_mental_health_trend.csv"},
    "transform": [
        {
            "calculate": "datum.country === 'Malaysia' ? 'Malaysia' : 'Other ASEAN countries'",
            "as": "country_group"
        }
    ],
    "width": "container",
    "height": 310,
    "encoding": {
        "x": {
            "field": "year",
            "type": "temporal",
            "title": "Year",
            "axis": {"format": "%Y"}
        },
        "y": {
            "field": "depression_prevalence",
            "type": "quantitative",
            "title": "Estimated depression prevalence (%)",
            "scale": {"zero": False}
        },
        "detail": {"field": "country", "type": "nominal"},
        "color": {
            "field": "country_group",
            "type": "nominal",
            "scale": {
                "domain": ["Malaysia", "Other ASEAN countries"],
                "range": ["#e08e79", "#b7c4d0"]
            },
            "title": None
        },
        "opacity": {
            "condition": {"test": "datum.country === 'Malaysia'", "value": 1},
            "value": 0.45
        },
        "tooltip": [
            {"field": "country", "type": "nominal"},
            {"field": "year", "type": "temporal", "format": "%Y"},
            {"field": "depression_prevalence", "type": "quantitative", "title": "Depression (%)", "format": ".2f"},
            {"field": "anxiety_prevalence", "type": "quantitative", "title": "Anxiety (%)", "format": ".2f"}
        ]
    },
    "mark": {"type": "line", "strokeWidth": 2.4}
}))


# 10 ASEAN MAP
write_spec("10_asean_map.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Geographic choropleth map of latest ASEAN depression prevalence.",
    "width": "container",
    "height": 310,
    "projection": {"type": "equalEarth"},
    "layer": [
        {
            "data": {
                "url": "https://cdn.jsdelivr.net/npm/vega-datasets@2.12.1/data/world-110m.json",
                "format": {"type": "topojson", "feature": "countries"}
            },
            "mark": {
                "type": "geoshape",
                "fill": "#e7edf4",
                "stroke": "#ffffff",
                "strokeWidth": 0.4
            }
        },
        {
            "data": {
                "url": "https://cdn.jsdelivr.net/npm/vega-datasets@2.12.1/data/world-110m.json",
                "format": {"type": "topojson", "feature": "countries"}
            },
            "transform": [
                {
                    "lookup": "id",
                    "from": {
                        "data": {"url": "data/processed/asean_latest_for_map.csv"},
                        "key": "m49",
                        "fields": [
                            "country",
                            "year",
                            "depression_prevalence",
                            "anxiety_prevalence",
                            "is_malaysia"
                        ]
                    }
                },
                {"filter": "isValid(datum.depression_prevalence)"}
            ],
            "mark": {
                "type": "geoshape",
                "stroke": "#ffffff",
                "strokeWidth": 1
            },
            "encoding": {
                "color": {
                    "field": "depression_prevalence",
                    "type": "quantitative",
                    "title": "Depression (%)",
                    "scale": {"scheme": "purples"}
                },
                "tooltip": [
                    {"field": "country", "type": "nominal"},
                    {"field": "year", "type": "quantitative"},
                    {"field": "depression_prevalence", "type": "quantitative", "title": "Depression (%)", "format": ".2f"},
                    {"field": "anxiety_prevalence", "type": "quantitative", "title": "Anxiety (%)", "format": ".2f"}
                ]
            }
        }
    ]
}))


# 11 ADOLESCENT WARNING SIGNS
write_spec("11_adolescent_warning_signs.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Malaysia adolescent warning signs profile.",
    "data": {"url": "data/processed/adolescent_warning_signs.csv"},
    "width": "container",
    "height": 320,
    "encoding": {
        "y": {
            "field": "indicator",
            "type": "nominal",
            "sort": "-x",
            "title": None,
            "axis": {"labelLimit": 220}
        },
        "x": {
            "field": "value",
            "type": "quantitative",
            "title": "Average reported share (%)",
            "scale": {"domain": [0, 100]}
        },
        "color": {
            "field": "type",
            "type": "nominal",
            "scale": {
                "domain": ["Warning sign", "Protective support"],
                "range": ["#e08e79", "#65a891"]
            },
            "title": "Indicator type"
        },
        "tooltip": [
            {"field": "indicator", "type": "nominal"},
            {"field": "type", "type": "nominal"},
            {"field": "value", "type": "quantitative", "title": "Share (%)", "format": ".1f"}
        ]
    },
    "layer": [
        {"mark": {"type": "bar", "cornerRadiusEnd": 8}},
        {
            "mark": {
                "type": "text",
                "align": "left",
                "dx": 6,
                "fontSize": 12,
                "fontWeight": 700,
                "color": "#132238"
            },
            "encoding": {
                "text": {"field": "value", "type": "quantitative", "format": ".1f"}
            }
        }
    ]
}))


# 12 ATTEMPTED SUICIDE AGE SEX
write_spec("12_attempted_suicide_age_sex.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Attempted suicide indicator by age group and sex.",
    "data": {"url": "data/processed/attempted_suicide_age_sex.csv"},
    "width": "container",
    "height": 290,
    "encoding": {
        "x": {
            "field": "age_group",
            "type": "nominal",
            "title": "Age group"
        },
        "y": {
            "field": "attempted_suicide",
            "type": "quantitative",
            "title": "Reported attempted suicide indicator (%)"
        },
        "color": {
            "field": "sex",
            "type": "nominal",
            "scale": {"range": ["#4f8fc0", "#e08e79", "#7c6bb0"]},
            "title": "Sex"
        },
        "xOffset": {"field": "sex"},
        "tooltip": [
            {"field": "year", "type": "quantitative"},
            {"field": "age_group", "type": "nominal"},
            {"field": "sex", "type": "nominal"},
            {"field": "attempted_suicide", "type": "quantitative", "title": "Indicator (%)", "format": ".1f"}
        ]
    },
    "mark": {"type": "bar", "cornerRadiusEnd": 6}
}))


# 13 PRESSURE PROFILE
write_spec("13_pressure_profile.json", with_config({
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Custom pressure profile combining indicators from multiple sources.",
    "data": {"url": "data/processed/pressure_profile.csv"},
    "width": "container",
    "height": 380,
    "encoding": {
        "y": {
            "field": "indicator",
            "type": "nominal",
            "sort": "-x",
            "title": None,
            "axis": {"labelLimit": 260}
        },
        "x": {
            "field": "value",
            "type": "quantitative",
            "title": "Percentage / indicator value",
            "scale": {"domain": [0, 100]}
        },
        "color": {
            "field": "direction",
            "type": "nominal",
            "scale": {
                "domain": ["pressure", "support"],
                "range": ["#e08e79", "#65a891"]
            },
            "title": "Meaning"
        },
        "row": {
            "field": "domain",
            "type": "nominal",
            "title": None,
            "header": {
                "labelFont": "Inter",
                "labelFontSize": 13,
                "labelFontWeight": 800,
                "labelColor": "#132238"
            }
        },
        "tooltip": [
            {"field": "domain", "type": "nominal"},
            {"field": "indicator", "type": "nominal"},
            {"field": "direction", "type": "nominal"},
            {"field": "value", "type": "quantitative", "format": ".1f"}
        ]
    },
    "layer": [
        {
            "mark": {"type": "rule", "strokeWidth": 5, "opacity": 0.28},
            "encoding": {
                "x": {"value": 0},
                "x2": {"field": "value"}
            }
        },
        {"mark": {"type": "circle", "size": 180}},
        {
            "mark": {
                "type": "text",
                "align": "left",
                "dx": 8,
                "fontSize": 12,
                "fontWeight": 700,
                "color": "#132238"
            },
            "encoding": {
                "text": {"field": "value", "type": "quantitative", "format": ".1f"}
            }
        }
    ]
}))


print("All Vega-Lite specs created.")