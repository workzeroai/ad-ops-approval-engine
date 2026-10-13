---
excalidraw-plugin: parsed
tags: [excalidraw]
---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==
# Drawing
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin/releases/tag/2.0.0",
  "elements": [
    {
      "id": "zone-human",
      "type": "rectangle",
      "x": 770,
      "y": 295.0,
      "width": 220,
      "height": 192.0,
      "angle": 0,
      "strokeColor": "#b45309",
      "backgroundColor": "#f8fafc",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "dashed",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1188391880,
      "version": 1,
      "versionNonce": 882375635,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "zone-human-label",
      "type": "text",
      "x": 786,
      "y": 305.0,
      "width": 92.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#b45309",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1569817570,
      "version": 1,
      "versionNonce": 1685214537,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "사람 승인 구간",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "left",
      "verticalAlign": "top",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "사람 승인 구간",
      "lineHeight": 1.25
    },
    {
      "id": "node-planned",
      "type": "rectangle",
      "x": 0,
      "y": 357.0,
      "width": 200,
      "height": 100,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "#f1f5f9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1811395954,
      "version": 1,
      "versionNonce": 767830841,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-planned"
        },
        {
          "type": "arrow",
          "id": "edge-planned-previewed-0"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-previewed",
      "type": "rectangle",
      "x": 440,
      "y": 357.0,
      "width": 160,
      "height": 100,
      "angle": 0,
      "strokeColor": "#0369a1",
      "backgroundColor": "#e0f2fe",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 725019444,
      "version": 1,
      "versionNonce": 1844533842,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-previewed"
        },
        {
          "type": "arrow",
          "id": "edge-planned-previewed-0"
        },
        {
          "type": "arrow",
          "id": "edge-previewed-approved-1"
        },
        {
          "type": "arrow",
          "id": "edge-previewed-blocked-4"
        },
        {
          "type": "arrow",
          "id": "edge-previewed-rejected-5"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-approved",
      "type": "rectangle",
      "x": 800,
      "y": 357.0,
      "width": 160,
      "height": 100,
      "angle": 0,
      "strokeColor": "#b45309",
      "backgroundColor": "#fef3c7",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 725961010,
      "version": 1,
      "versionNonce": 373258649,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-approved"
        },
        {
          "type": "arrow",
          "id": "edge-previewed-approved-1"
        },
        {
          "type": "arrow",
          "id": "edge-approved-applied-2"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-applied",
      "type": "rectangle",
      "x": 1140,
      "y": 357.0,
      "width": 160,
      "height": 100,
      "angle": 0,
      "strokeColor": "#3730a3",
      "backgroundColor": "#e0e7ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1874968988,
      "version": 1,
      "versionNonce": 207678939,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-applied"
        },
        {
          "type": "arrow",
          "id": "edge-approved-applied-2"
        },
        {
          "type": "arrow",
          "id": "edge-applied-verified-3"
        },
        {
          "type": "arrow",
          "id": "edge-applied-failed-6"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-verified",
      "type": "rectangle",
      "x": 1540,
      "y": 357.0,
      "width": 160,
      "height": 100,
      "angle": 0,
      "strokeColor": "#15803d",
      "backgroundColor": "#dcfce7",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1728662868,
      "version": 1,
      "versionNonce": 1628928971,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-verified"
        },
        {
          "type": "arrow",
          "id": "edge-applied-verified-3"
        },
        {
          "type": "arrow",
          "id": "edge-verified-rolledback-8"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-blocked",
      "type": "ellipse",
      "x": 360,
      "y": 97.0,
      "width": 300,
      "height": 160,
      "angle": 0,
      "strokeColor": "#b45309",
      "backgroundColor": "#fef3c7",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 1770555940,
      "version": 1,
      "versionNonce": 1023065923,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-blocked"
        },
        {
          "type": "arrow",
          "id": "edge-previewed-blocked-4"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-rejected",
      "type": "ellipse",
      "x": 420,
      "y": 577.0,
      "width": 180,
      "height": 120,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "#f1f5f9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 158231374,
      "version": 1,
      "versionNonce": 1152378572,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-rejected"
        },
        {
          "type": "arrow",
          "id": "edge-previewed-rejected-5"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-failed",
      "type": "rectangle",
      "x": 1120,
      "y": 577.0,
      "width": 220,
      "height": 100,
      "angle": 0,
      "strokeColor": "#b91c1c",
      "backgroundColor": "#fee2e2",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 647468931,
      "version": 1,
      "versionNonce": 233584594,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-failed"
        },
        {
          "type": "arrow",
          "id": "edge-applied-failed-6"
        },
        {
          "type": "arrow",
          "id": "edge-failed-skipped-7"
        },
        {
          "type": "arrow",
          "id": "edge-failed-rolledback-9"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-skipped",
      "type": "ellipse",
      "x": 1100,
      "y": 797.0,
      "width": 260,
      "height": 120,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "#f1f5f9",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 738715286,
      "version": 1,
      "versionNonce": 1243867611,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-skipped"
        },
        {
          "type": "arrow",
          "id": "edge-failed-skipped-7"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-rolledback",
      "type": "rectangle",
      "x": 1520,
      "y": 577.0,
      "width": 200,
      "height": 100,
      "angle": 0,
      "strokeColor": "#b91c1c",
      "backgroundColor": "#fee2e2",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1119695138,
      "version": 1,
      "versionNonce": 1248693506,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-rolledback"
        },
        {
          "type": "arrow",
          "id": "edge-verified-rolledback-8"
        },
        {
          "type": "arrow",
          "id": "edge-failed-rolledback-9"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "edge-planned-previewed-0",
      "type": "arrow",
      "x": 208.0,
      "y": 407.0,
      "width": 224.0,
      "height": 0.0,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "grp-edge-planned-previewed-0"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 59471497,
      "version": 1,
      "versionNonce": 1617277727,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "points": [
        [
          0.0,
          0.0
        ],
        [
          224.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-planned",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-previewed",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-planned-previewed-0",
      "type": "text",
      "x": 292.5,
      "y": 379.0,
      "width": 55.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [
        "grp-edge-planned-previewed-0"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 716110922,
      "version": 1,
      "versionNonce": 1110027,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "preview",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "preview",
      "lineHeight": 1.25
    },
    {
      "id": "edge-previewed-approved-1",
      "type": "arrow",
      "x": 608.0,
      "y": 407.0,
      "width": 184.0,
      "height": 0.0,
      "angle": 0,
      "strokeColor": "#15803d",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "grp-edge-previewed-approved-1"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1610571083,
      "version": 1,
      "versionNonce": 1702829099,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "points": [
        [
          0.0,
          0.0
        ],
        [
          184.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-previewed",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-approved",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-previewed-approved-1",
      "type": "text",
      "x": 686.0,
      "y": 379.0,
      "width": 28.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#15803d",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [
        "grp-edge-previewed-approved-1"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1194434252,
      "version": 1,
      "versionNonce": 1693047854,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "승인",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "승인",
      "lineHeight": 1.25
    },
    {
      "id": "edge-approved-applied-2",
      "type": "arrow",
      "x": 968.0,
      "y": 407.0,
      "width": 164.0,
      "height": 0.0,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "grp-edge-approved-applied-2"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 599724244,
      "version": 1,
      "versionNonce": 590921837,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "points": [
        [
          0.0,
          0.0
        ],
        [
          164.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-approved",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-applied",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-approved-applied-2",
      "type": "text",
      "x": 1031.5,
      "y": 379.0,
      "width": 37.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [
        "grp-edge-approved-applied-2"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 242367322,
      "version": 1,
      "versionNonce": 553174091,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "apply",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "apply",
      "lineHeight": 1.25
    },
    {
      "id": "edge-applied-verified-3",
      "type": "arrow",
      "x": 1308.0,
      "y": 407.0,
      "width": 224.0,
      "height": 0.0,
      "angle": 0,
      "strokeColor": "#15803d",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "grp-edge-applied-verified-3"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1963725803,
      "version": 1,
      "versionNonce": 1804225047,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "points": [
        [
          0.0,
          0.0
        ],
        [
          224.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-applied",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-verified",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-applied-verified-3",
      "type": "text",
      "x": 1400.0,
      "y": 379.0,
      "width": 40.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#15803d",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [
        "grp-edge-applied-verified-3"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 150724673,
      "version": 1,
      "versionNonce": 310509242,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "verify",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "verify",
      "lineHeight": 1.25
    },
    {
      "id": "edge-previewed-blocked-4",
      "type": "arrow",
      "x": 515.0,
      "y": 349.0,
      "width": 0.0,
      "height": 84.04,
      "angle": 0,
      "strokeColor": "#b45309",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "grp-edge-previewed-blocked-4"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1846764418,
      "version": 1,
      "versionNonce": 1589938751,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "points": [
        [
          0.0,
          0.0
        ],
        [
          0.0,
          -84.04
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-previewed",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-blocked",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-previewed-blocked-4",
      "type": "text",
      "x": 523.0,
      "y": 296.98,
      "width": 56.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#b45309",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [
        "grp-edge-previewed-blocked-4"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1574663878,
      "version": 1,
      "versionNonce": 1280201878,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "안전장치",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "안전장치",
      "lineHeight": 1.25
    },
    {
      "id": "edge-previewed-rejected-5",
      "type": "arrow",
      "x": 515.0,
      "y": 465.0,
      "width": 0.0,
      "height": 104.09,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "grp-edge-previewed-rejected-5"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 971653209,
      "version": 1,
      "versionNonce": 1624245475,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "points": [
        [
          0.0,
          0.0
        ],
        [
          0.0,
          104.09
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-previewed",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-rejected",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-previewed-rejected-5",
      "type": "text",
      "x": 523.0,
      "y": 507.05,
      "width": 28.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [
        "grp-edge-previewed-rejected-5"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 975393207,
      "version": 1,
      "versionNonce": 304061247,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "거절",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "거절",
      "lineHeight": 1.25
    },
    {
      "id": "edge-applied-failed-6",
      "type": "arrow",
      "x": 1225.0,
      "y": 465.0,
      "width": 0.0,
      "height": 104.0,
      "angle": 0,
      "strokeColor": "#b91c1c",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "grp-edge-applied-failed-6"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 965814350,
      "version": 1,
      "versionNonce": 1906397350,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "points": [
        [
          0.0,
          0.0
        ],
        [
          0.0,
          104.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-applied",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-failed",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-applied-failed-6",
      "type": "text",
      "x": 1233.0,
      "y": 507.0,
      "width": 42.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#b91c1c",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [
        "grp-edge-applied-failed-6"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 287782717,
      "version": 1,
      "versionNonce": 885152526,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "불일치",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "불일치",
      "lineHeight": 1.25
    },
    {
      "id": "edge-failed-skipped-7",
      "type": "arrow",
      "x": 1230.0,
      "y": 685.0,
      "width": 0.0,
      "height": 104.0,
      "angle": 0,
      "strokeColor": "#b91c1c",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "dashed",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "grp-edge-failed-skipped-7"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 760754190,
      "version": 1,
      "versionNonce": 606929153,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "points": [
        [
          0.0,
          0.0
        ],
        [
          0.0,
          104.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-failed",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-skipped",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-failed-skipped-7",
      "type": "text",
      "x": 1238.0,
      "y": 727.0,
      "width": 74.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#b91c1c",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [
        "grp-edge-failed-skipped-7"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 298179906,
      "version": 1,
      "versionNonce": 1269932750,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "나머지 중단",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "나머지 중단",
      "lineHeight": 1.25
    },
    {
      "id": "edge-verified-rolledback-8",
      "type": "arrow",
      "x": 1620.0,
      "y": 465.0,
      "width": 0.0,
      "height": 104.0,
      "angle": 0,
      "strokeColor": "#b91c1c",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "grp-edge-verified-rolledback-8"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1094503458,
      "version": 1,
      "versionNonce": 1131782657,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "points": [
        [
          0.0,
          0.0
        ],
        [
          0.0,
          104.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-verified",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-rolledback",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-verified-rolledback-8",
      "type": "text",
      "x": 1628.0,
      "y": 507.0,
      "width": 55.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#b91c1c",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [
        "grp-edge-verified-rolledback-8"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 141317943,
      "version": 1,
      "versionNonce": 682364205,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "rollback",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "rollback",
      "lineHeight": 1.25
    },
    {
      "id": "edge-failed-rolledback-9",
      "type": "arrow",
      "x": 1348.0,
      "y": 627.0,
      "width": 164.0,
      "height": 0.0,
      "angle": 0,
      "strokeColor": "#b91c1c",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "grp-edge-failed-rolledback-9"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 493759374,
      "version": 1,
      "versionNonce": 208254487,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "points": [
        [
          0.0,
          0.0
        ],
        [
          164.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-failed",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-rolledback",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-failed-rolledback-9",
      "type": "text",
      "x": 1402.5,
      "y": 599.0,
      "width": 55.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#b91c1c",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [
        "grp-edge-failed-rolledback-9"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1028769541,
      "version": 1,
      "versionNonce": 250904414,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "rollback",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "rollback",
      "lineHeight": 1.25
    },
    {
      "id": "text-planned",
      "type": "text",
      "x": 27.0,
      "y": 382.0,
      "width": 146.0,
      "height": 50.0,
      "angle": 0,
      "strokeColor": "#0f172a",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 803381432,
      "version": 1,
      "versionNonce": 844439166,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "planned\n규칙이 만든 조정안",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-planned",
      "originalText": "planned\n규칙이 만든 조정안",
      "lineHeight": 1.25
    },
    {
      "id": "text-previewed",
      "type": "text",
      "x": 464.0,
      "y": 382.0,
      "width": 112.0,
      "height": 50.0,
      "angle": 0,
      "strokeColor": "#0f172a",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 667195261,
      "version": 1,
      "versionNonce": 1694874318,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "previewed\n현재 값 재조회",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-previewed",
      "originalText": "previewed\n현재 값 재조회",
      "lineHeight": 1.25
    },
    {
      "id": "text-approved",
      "type": "text",
      "x": 835.5,
      "y": 382.0,
      "width": 89.0,
      "height": 50.0,
      "angle": 0,
      "strokeColor": "#0f172a",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 155901939,
      "version": 1,
      "versionNonce": 264267381,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "approved\n사람 승인",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-approved",
      "originalText": "approved\n사람 승인",
      "lineHeight": 1.25
    },
    {
      "id": "text-applied",
      "type": "text",
      "x": 1185.0,
      "y": 382.0,
      "width": 70.0,
      "height": 50.0,
      "angle": 0,
      "strokeColor": "#0f172a",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1279841777,
      "version": 1,
      "versionNonce": 528827114,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "applied\nAPI 반영",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-applied",
      "originalText": "applied\nAPI 반영",
      "lineHeight": 1.25
    },
    {
      "id": "text-verified",
      "type": "text",
      "x": 1564.0,
      "y": 382.0,
      "width": 112.0,
      "height": 50.0,
      "angle": 0,
      "strokeColor": "#0f172a",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 226870970,
      "version": 1,
      "versionNonce": 1946912256,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "verified\n재조회 값 일치",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-verified",
      "originalText": "verified\n재조회 값 일치",
      "lineHeight": 1.25
    },
    {
      "id": "text-blocked",
      "type": "text",
      "x": 434.5,
      "y": 139.5,
      "width": 151.0,
      "height": 75.0,
      "angle": 0,
      "strokeColor": "#0f172a",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 987018141,
      "version": 1,
      "versionNonce": 1824315561,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "blocked\n변경 폭·하한/상한\n학습 기간·일일 건수",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 66.4,
      "containerId": "node-blocked",
      "originalText": "blocked\n변경 폭·하한/상한\n학습 기간·일일 건수",
      "lineHeight": 1.25
    },
    {
      "id": "text-rejected",
      "type": "text",
      "x": 471.0,
      "y": 612.0,
      "width": 78.0,
      "height": 50.0,
      "angle": 0,
      "strokeColor": "#0f172a",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1196651841,
      "version": 1,
      "versionNonce": 1959600579,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "rejected\n승인 거절",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-rejected",
      "originalText": "rejected\n승인 거절",
      "lineHeight": 1.25
    },
    {
      "id": "text-failed",
      "type": "text",
      "x": 1147.5,
      "y": 602.0,
      "width": 165.0,
      "height": 50.0,
      "angle": 0,
      "strokeColor": "#0f172a",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1535205559,
      "version": 1,
      "versionNonce": 1353125512,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "failed\n검증 불일치·API 오류",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-failed",
      "originalText": "failed\n검증 불일치·API 오류",
      "lineHeight": 1.25
    },
    {
      "id": "text-skipped",
      "type": "text",
      "x": 1165.5,
      "y": 832.0,
      "width": 129.0,
      "height": 50.0,
      "angle": 0,
      "strokeColor": "#0f172a",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 435498732,
      "version": 1,
      "versionNonce": 1648771294,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "skipped\n앞선 실패로 중단",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-skipped",
      "originalText": "skipped\n앞선 실패로 중단",
      "lineHeight": 1.25
    },
    {
      "id": "text-rolledback",
      "type": "text",
      "x": 1544.5,
      "y": 602.0,
      "width": 151.0,
      "height": 50.0,
      "angle": 0,
      "strokeColor": "#0f172a",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1459383776,
      "version": 1,
      "versionNonce": 99832135,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "rolled_back\n이전 값 복원·재조회",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-rolledback",
      "originalText": "rolled_back\n이전 값 복원·재조회",
      "lineHeight": 1.25
    },
    {
      "id": "title",
      "type": "text",
      "x": 0,
      "y": 0.0,
      "width": 230.0,
      "height": 35.0,
      "angle": 0,
      "strokeColor": "#0f172a",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 159451258,
      "version": 1,
      "versionNonce": 1971650405,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "상태 전이와 안전장치",
      "fontSize": 28,
      "fontFamily": 2,
      "textAlign": "left",
      "verticalAlign": "top",
      "baseline": 22.96,
      "containerId": null,
      "originalText": "상태 전이와 안전장치",
      "lineHeight": 1.25
    },
    {
      "id": "subtitle",
      "type": "text",
      "x": 0,
      "y": 41.0,
      "width": 560.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#64748b",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1919961959,
      "version": 1,
      "versionNonce": 869340623,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "승인 없이 applied로 가는 길은 없다 · 검증 실패는 실행 전체를 멈추고 실행 ID로 되돌린다",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "left",
      "verticalAlign": "top",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "승인 없이 applied로 가는 길은 없다 · 검증 실패는 실행 전체를 멈추고 실행 ID로 되돌린다",
      "lineHeight": 1.25
    }
  ],
  "appState": {
    "gridSize": null,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```
%%
# Text Elements
사람 승인 구간 ^zone-human-label
preview ^label-edge-planned-previewed-0
승인 ^label-edge-previewed-approved-1
apply ^label-edge-approved-applied-2
verify ^label-edge-applied-verified-3
안전장치 ^label-edge-previewed-blocked-4
거절 ^label-edge-previewed-rejected-5
불일치 ^label-edge-applied-failed-6
나머지 중단 ^label-edge-failed-skipped-7
rollback ^label-edge-verified-rolledback-8
rollback ^label-edge-failed-rolledback-9
planned
규칙이 만든 조정안 ^text-planned
previewed
현재 값 재조회 ^text-previewed
approved
사람 승인 ^text-approved
applied
API 반영 ^text-applied
verified
재조회 값 일치 ^text-verified
blocked
변경 폭·하한/상한
학습 기간·일일 건수 ^text-blocked
rejected
승인 거절 ^text-rejected
failed
검증 불일치·API 오류 ^text-failed
skipped
앞선 실패로 중단 ^text-skipped
rolled_back
이전 값 복원·재조회 ^text-rolledback
상태 전이와 안전장치 ^title
승인 없이 applied로 가는 길은 없다 · 검증 실패는 실행 전체를 멈추고 실행 ID로 되돌린다 ^subtitle
%%
