---
ingested: 2026-04-30
sha256: 5ec47300890e6333
source_url: hermes-skill://fine-report-cpt
title: FineReport (帆软报表) CPT File Analysis & Development
---
---
name: fine-report-cpt
description: Analyze, read, and modify FineReport (帆软报表) CPT template files — XML structure, attribute meanings, unit systems, and common modification patterns.
tags: [finereport, 帆软, cpt, report, xml]
---

# FineReport (帆软报表) CPT File Analysis & Development

## Overview
CPT files are FineReport's report template format. They are standard XML files (UTF-8) that define data sources, parameters, cell layouts, charts, styles, and page settings.

## Locating Uploaded CPT Files
When a CPT file is received via messaging (QQ, etc.), it may not appear in the working directory. Check:
```
/home/agentuser/.hermes/cache/documents/
```
Files there have names like `doc_<hash>_<originalname`. Verify with `file` command — should show "XML 1.0 document".

## XML Structure Hierarchy

```
WorkBook (root)
├── TableDataMap          — Data source definitions
│   └── TableData[]       — Individual datasets
├── ElementCaseMobileAttr — Mobile rendering settings
├── Report                — Main report sheet
│   ├── ReportPageAttr    — Page/repeat settings
│   ├── RowHeight         — Default row height
│   ├── ColumnWidth       — Default column width
│   ├── FloatElementList  — Floating elements (charts)
│   ├── CellElementList   — Cell grid (C elements)
│   └── ReportAttrSet     — Page header/footer
├── ReportParameterAttr   — Parameter panel config
│   └── ParameterUI       — Parameter form widgets
├── StyleList             — Named style definitions
├── DesensitizationList   — Data masking rules
├── DesignerVersion       — Designer version tag
├── PreviewType           — Preview mode
├── TemplateThemeAttrMark — Theme (e.g. "经典浅灰")
├── StrategyConfigsAttr   — Dataset caching strategy
├── ForkIdAttrMark        — Branch ID
├── TemplateCloudInfoAttrMark — Cloud metadata
└── TemplateIdAttMark     — Template UUID
```

## Key Attribute Meanings (Verified + Probable)

### WorkBook Root
| Attribute | Meaning |
|-----------|---------|
| `xmlVersion` | XML schema version (e.g. "20211223") |
| `releaseVersion` | FineReport designer version (e.g. "11.0.0") |

### TableData (Dataset)
| Attribute | Meaning |
|-----------|---------|
| `name` | Dataset name, referenced in cells via `dsName` |
| `class` | `DBTableData`=SQL query, `EmbeddedTableData`=inline data, `NameTableData`=server dataset ref |
| `maxMemRowCount` | Max rows cached in memory, -1=unlimited |
| `desensitizeOpen` | Enable data masking |

### Parameter
| Attribute | Meaning |
|-----------|---------|
| `Attributes.name` | Parameter name, used in SQL as `${paramName}` |
| `O` (child text) | Default parameter value |

### Cell Element (`<C>`)
| Attribute | Meaning |
|-----------|---------|
| `c` | Column index (0-based) |
| `r` | Row index (0-based) |
| `cs` | Column span (merge across columns) |
| `rs` | Row span (merge across rows) |
| `s` | Style index into StyleList |

### Cell Value (`<O>` under `<C>`)
| Attribute | Meaning |
|-----------|---------|
| `t` (absent) | Plain text/static value |
| `t=DSColumn` | Data column binding (from dataset) |
| `t=CC` | Chart component |
| `t=XMLable` | Serializable object |
| `class=com.fr.base.Formula` | Formula expression |

### Data Column Attributes (when O.t=DSColumn)
| Attribute | Meaning |
|-----------|---------|
| `dsName` | Source dataset name |
| `columnName` | Source column/field name |

### Expand Direction
| Attribute | Meaning |
|-----------|---------|
| `dir=0` | Vertical expansion (expand downward) |
| `dir=1` | Horizontal expansion (expand rightward) |
| `left` | Left parent cell reference (e.g. "B10") |
| `leftParentDefault=false` | Custom left parent override |

### FloatElement (Floating Chart)
| Attribute | Meaning |
|-----------|---------|
| `FloatElementName.name` | Floating element name |
| `Location.leftDistance/topDistance` | Position (likely EMU units) |
| `Location.width/height` | Size (likely EMU units) |
| `Chart.chartClass` | Chart engine class (VanChart = new chart engine) |
| `ChangeAttr.enable` | Chart auto-rotation/carousel |
| `Style.index` | Style reference index |

### StyleList
| Attribute | Meaning |
|-----------|---------|
| `FRFont.name` | Font family (simhei=黑体, SimSun=宋体) |
| `FRFont.size` | Font size in 1/4 point units (72 → 18pt) |
| `FRFont.style` | 0=regular, 1=bold |
| `Background.name` | `NullBackground`=none, `ColorBackground`=solid color |
| `horizontal_alignment` | 0=left (probable, needs confirmation) |
| `Format.roundingMode=6` | Likely HALF_EVEN (banker's rounding) |

### Page Settings
| Attribute | Meaning |
|-----------|---------|
| `HR F/T` | Repeat header rows: From row F, To row T |
| `UPFCR COLUMN/ROW` | Column/Row freeze on pagination |
| `USE REPEAT` | Repeat frozen rows on each page |
| `USE PAGE` | Enable pagination |
| `USE WRITE` | Enable fill/write mode |
| `RowHeight.defaultValue` | Default row height in EMU (723900 ≈ 2cm) |
| `ColumnWidth.defaultValue` | Default column width in EMU (2743200 ≈ 7.6cm) |

### Parameter Panel
| Attribute | Meaning |
|-----------|---------|
| `showWindow` | Show parameter dialog |
| `delayPlaying` | Delay query until parameter submitted |
| `windowPosition` | Parameter window position (1=center?) |
| `useParamsTemplate` | Use parameter UI template |
| `DesignAttr width/height` | Parameter panel design size in pixels |
| `InnerWidget.class` | Widget type: ComboBox, DateEditor, ComboCheckBox, Label, FormSubmitButton |

### Caching Strategy (StrategyConfig)
| Attribute | Meaning |
|-----------|---------|
| `dsName` | Dataset this config applies to |
| `enabled` | Caching enabled |
| `timeToLive` | Cache TTL in milliseconds (1500000=25min) |
| `timeToIdle` | Cache idle timeout in ms (86400000=24h) |
| `updateInterval` | Refresh interval in ms |
| `updateSchema` | Cron expression for scheduled refresh |

## Unit System
- **Position/Size (Location, RowHeight, ColumnWidth)**: Likely EMU (English Metric Units). 1 inch = 914400 EMU, 1 cm = 360000 EMU
- **Font size**: 1/4 point units. Value ÷ 4 = actual pt size (72 → 18pt)
- **Color**: Negative integers representing RGB in signed 32-bit format. Convert: `value & 0xFFFFFF`

## Analytical Approach for Unknown XML Formats
Use this Python snippet to extract all unique tag→attribute→value mappings:
```python
import xml.etree.ElementTree as ET
from collections import defaultdict

tree = ET.parse('file.cpt')
root = tree.getroot()
tag_attrs = defaultdict(lambda: defaultdict(set))

def collect(elem):
    for k, v in elem.attrib.items():
        if len(v) > 50: v = v[:50] + '...'
        tag_attrs[elem.tag][k].add(v)
    for child in elem:
        collect(child)

collect(root)
```

## SQL Parameter Syntax in CPT
- `${paramName}` — direct parameter substitution
- `${IF(LEN(param)==0, "", "and col='" + param + "'")}` — conditional SQL fragment
- Parameters are defined in TableData/Parameters with name and default value

## Common Modification Patterns
- **Change SQL query**: Edit `<Query>` CDATA content in TableData
- **Add parameter**: Add `<Parameter>` under TableData/Parameters, update SQL with `${newParam}`
- **Change cell binding**: Modify `O/Attributes dsName` and `columnName`
- **Change style**: Update `C.s` index or modify StyleList entries
- **Change chart**: Modify FloatElement → Chart subtree
- **Add cell**: Add `<C>` element with c, r, s attributes and children (O, PrivilegeControl, Expand)

## Pitfalls
- CPT files can be very large (20K+ lines). Use offset/limit when reading.
- The `ColumnNames` in EmbeddedTableData uses `,,` as delimiter (commas within names are escaped).
- Cell elements only store non-empty cells; empty cells are implied by the grid.
- Font size units are NOT points — must divide by 4.
- Location/size values are in EMU, not pixels or cm — must convert.
- Some attribute meanings are inferred but not yet confirmed by a FineReport expert — validate before critical edits.
