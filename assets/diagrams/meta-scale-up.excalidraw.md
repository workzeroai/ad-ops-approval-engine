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
      "id": "node-collect",
      "type": "rectangle",
      "x": 0,
      "y": 377.0,
      "width": 200,
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
      "seed": 1623294841,
      "version": 1,
      "versionNonce": 1830165425,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-collect"
        },
        {
          "type": "arrow",
          "id": "edge-collect-win-0"
        },
        {
          "type": "arrow",
          "id": "edge-collect-lose-1"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-win",
      "type": "diamond",
      "x": 280,
      "y": 97.0,
      "width": 400,
      "height": 180,
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
      "seed": 73341917,
      "version": 1,
      "versionNonce": 241016130,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-win"
        },
        {
          "type": "arrow",
          "id": "edge-collect-win-0"
        },
        {
          "type": "arrow",
          "id": "edge-win-up-2"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-lose",
      "type": "diamond",
      "x": 320,
      "y": 617.0,
      "width": 320,
      "height": 180,
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
      "seed": 1278768010,
      "version": 1,
      "versionNonce": 773900390,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-lose"
        },
        {
          "type": "arrow",
          "id": "edge-collect-lose-1"
        },
        {
          "type": "arrow",
          "id": "edge-lose-pause-3"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-up",
      "type": "rectangle",
      "x": 800,
      "y": 137.0,
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
      "seed": 1865634026,
      "version": 1,
      "versionNonce": 370075647,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-up"
        },
        {
          "type": "arrow",
          "id": "edge-win-up-2"
        },
        {
          "type": "arrow",
          "id": "edge-up-cand-4"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-pause",
      "type": "rectangle",
      "x": 800,
      "y": 677.0,
      "width": 160,
      "height": 80,
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
      "seed": 176315937,
      "version": 1,
      "versionNonce": 1588308495,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-pause"
        },
        {
          "type": "arrow",
          "id": "edge-lose-pause-3"
        },
        {
          "type": "arrow",
          "id": "edge-pause-cand-5"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-cand",
      "type": "rectangle",
      "x": 1020,
      "y": 377.0,
      "width": 200,
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
      "seed": 175742839,
      "version": 1,
      "versionNonce": 544311603,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-cand"
        },
        {
          "type": "arrow",
          "id": "edge-up-cand-4"
        },
        {
          "type": "arrow",
          "id": "edge-pause-cand-5"
        },
        {
          "type": "arrow",
          "id": "edge-cand-guard-6"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-guard",
      "type": "diamond",
      "x": 1280,
      "y": 337.0,
      "width": 380,
      "height": 180,
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
        "type": 2
      },
      "seed": 1463393895,
      "version": 1,
      "versionNonce": 1376505559,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-guard"
        },
        {
          "type": "arrow",
          "id": "edge-cand-guard-6"
        },
        {
          "type": "arrow",
          "id": "edge-guard-block-7"
        },
        {
          "type": "arrow",
          "id": "edge-guard-approve-8"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-block",
      "type": "ellipse",
      "x": 1360,
      "y": 657.0,
      "width": 240,
      "height": 120,
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
        "type": 2
      },
      "seed": 850103712,
      "version": 1,
      "versionNonce": 203387220,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-block"
        },
        {
          "type": "arrow",
          "id": "edge-guard-block-7"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "node-approve",
      "type": "rectangle",
      "x": 1800,
      "y": 377.0,
      "width": 200,
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
      "seed": 923566162,
      "version": 1,
      "versionNonce": 1965813705,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "text-approve"
        },
        {
          "type": "arrow",
          "id": "edge-guard-approve-8"
        }
      ],
      "updated": 1760000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "edge-collect-win-0",
      "type": "arrow",
      "x": 208.0,
      "y": 427.0,
      "width": 272.0,
      "height": 142.0,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "transparent",
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
      "seed": 90614329,
      "version": 1,
      "versionNonce": 1693162925,
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
          208.0,
          0.0
        ],
        [
          272.0,
          -64.0
        ],
        [
          272.0,
          -142.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-collect",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-win",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "edge-collect-lose-1",
      "type": "arrow",
      "x": 208.0,
      "y": 427.0,
      "width": 272.0,
      "height": 182.0,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "transparent",
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
      "seed": 894274310,
      "version": 1,
      "versionNonce": 21241189,
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
          208.0,
          0.0
        ],
        [
          272.0,
          64.0
        ],
        [
          272.0,
          182.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-collect",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-lose",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "edge-win-up-2",
      "type": "arrow",
      "x": 688.0,
      "y": 187.0,
      "width": 104.0,
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
        "grp-edge-win-up-2"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 968700954,
      "version": 1,
      "versionNonce": 1381148436,
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
          104.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-win",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-up",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-win-up-2",
      "type": "text",
      "x": 733.0,
      "y": 159.0,
      "width": 14.0,
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
        "grp-edge-win-up-2"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 742568782,
      "version": 1,
      "versionNonce": 957646970,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "예",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "예",
      "lineHeight": 1.25
    },
    {
      "id": "edge-lose-pause-3",
      "type": "arrow",
      "x": 639.11,
      "y": 712.0,
      "width": 152.89,
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
        "grp-edge-lose-pause-3"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 396110125,
      "version": 1,
      "versionNonce": 80159499,
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
          152.89,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-lose",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-pause",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-lose-pause-3",
      "type": "text",
      "x": 708.56,
      "y": 684.0,
      "width": 14.0,
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
        "grp-edge-lose-pause-3"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 506649155,
      "version": 1,
      "versionNonce": 388062307,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "예",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "예",
      "lineHeight": 1.25
    },
    {
      "id": "edge-up-cand-4",
      "type": "arrow",
      "x": 968.0,
      "y": 187.0,
      "width": 152.0,
      "height": 182.0,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "transparent",
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
      "seed": 102544310,
      "version": 1,
      "versionNonce": 1512344995,
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
          88.0,
          0.0
        ],
        [
          152.0,
          64.0
        ],
        [
          152.0,
          182.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-up",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-cand",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "edge-pause-cand-5",
      "type": "arrow",
      "x": 968.0,
      "y": 717.0,
      "width": 152.0,
      "height": 232.0,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "transparent",
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
      "seed": 1517756513,
      "version": 1,
      "versionNonce": 236900348,
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
          88.0,
          0.0
        ],
        [
          152.0,
          -64.0
        ],
        [
          152.0,
          -232.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-pause",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-cand",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "edge-cand-guard-6",
      "type": "arrow",
      "x": 1228.0,
      "y": 427.0,
      "width": 44.0,
      "height": 0.0,
      "angle": 0,
      "strokeColor": "#334155",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1568505732,
      "version": 1,
      "versionNonce": 765853848,
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
          44.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-cand",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-guard",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "edge-guard-block-7",
      "type": "arrow",
      "x": 1475.0,
      "y": 522.63,
      "width": 0.0,
      "height": 126.42,
      "angle": 0,
      "strokeColor": "#b91c1c",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "grp-edge-guard-block-7"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1306096183,
      "version": 1,
      "versionNonce": 1286632786,
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
          126.42
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-guard",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-block",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-guard-block-7",
      "type": "text",
      "x": 1483.0,
      "y": 575.84,
      "width": 28.0,
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
        "grp-edge-guard-block-7"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1564319349,
      "version": 1,
      "versionNonce": 1576494387,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "위반",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "위반",
      "lineHeight": 1.25
    },
    {
      "id": "edge-guard-approve-8",
      "type": "arrow",
      "x": 1668.0,
      "y": 427.0,
      "width": 124.0,
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
        "grp-edge-guard-approve-8"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 617392217,
      "version": 1,
      "versionNonce": 675999854,
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
          124.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-guard",
        "focus": 0,
        "gap": 8
      },
      "endBinding": {
        "elementId": "node-approve",
        "focus": 0,
        "gap": 8
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "label-edge-guard-approve-8",
      "type": "text",
      "x": 1716.0,
      "y": 399.0,
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
        "grp-edge-guard-approve-8"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 19254013,
      "version": 1,
      "versionNonce": 138538823,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "통과",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "통과",
      "lineHeight": 1.25
    },
    {
      "id": "text-collect",
      "type": "text",
      "x": 24.0,
      "y": 402.0,
      "width": 152.0,
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
      "seed": 1270816535,
      "version": 1,
      "versionNonce": 1987845839,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "소재 단위 일별 실적\n→ 세트 단위로 합산",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-collect",
      "originalText": "소재 단위 일별 실적\n→ 세트 단위로 합산",
      "lineHeight": 1.25
    },
    {
      "id": "text-win",
      "type": "text",
      "x": 387.5,
      "y": 149.5,
      "width": 185.0,
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
      "seed": 1596153992,
      "version": 1,
      "versionNonce": 65457942,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "위닝 조건?\nROAS ≥ 350%\n전환 ≥ 20건 · 상위 절반",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 66.4,
      "containerId": "node-win",
      "originalText": "위닝 조건?\nROAS ≥ 350%\n전환 ≥ 20건 · 상위 절반",
      "lineHeight": 1.25
    },
    {
      "id": "text-lose",
      "type": "text",
      "x": 368.5,
      "y": 669.5,
      "width": 223.0,
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
      "seed": 589837568,
      "version": 1,
      "versionNonce": 798776628,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "소재 조건?\nCTR -30%↓ & 빈도 3.5↑\n또는 ROAS < 70%",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 66.4,
      "containerId": "node-lose",
      "originalText": "소재 조건?\nCTR -30%↓ & 빈도 3.5↑\n또는 ROAS < 70%",
      "lineHeight": 1.25
    },
    {
      "id": "text-up",
      "type": "text",
      "x": 834.0,
      "y": 162.0,
      "width": 92.0,
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
      "seed": 1951724595,
      "version": 1,
      "versionNonce": 1825533613,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "세트 예산\n+20% 후보",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-up",
      "originalText": "세트 예산\n+20% 후보",
      "lineHeight": 1.25
    },
    {
      "id": "text-pause",
      "type": "text",
      "x": 824.0,
      "y": 704.5,
      "width": 112.0,
      "height": 25.0,
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
      "seed": 770247878,
      "version": 1,
      "versionNonce": 1256188812,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "소재 중지 후보",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 16.4,
      "containerId": "node-pause",
      "originalText": "소재 중지 후보",
      "lineHeight": 1.25
    },
    {
      "id": "text-cand",
      "type": "text",
      "x": 1044.5,
      "y": 402.0,
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
      "seed": 713256248,
      "version": 1,
      "versionNonce": 70100317,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "조정안\n근거 문장 자동 생성",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-cand",
      "originalText": "조정안\n근거 문장 자동 생성",
      "lineHeight": 1.25
    },
    {
      "id": "text-guard",
      "type": "text",
      "x": 1385.5,
      "y": 389.5,
      "width": 169.0,
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
      "seed": 157038132,
      "version": 1,
      "versionNonce": 178206651,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "안전장치\n변경 폭 ≤ 20%\n쿨다운 3일 · 하루 6건",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 66.4,
      "containerId": "node-guard",
      "originalText": "안전장치\n변경 폭 ≤ 20%\n쿨다운 3일 · 하루 6건",
      "lineHeight": 1.25
    },
    {
      "id": "text-block",
      "type": "text",
      "x": 1424.0,
      "y": 692.0,
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
      "seed": 1878503162,
      "version": 1,
      "versionNonce": 33795304,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "차단\n학습 기간 보호",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-block",
      "originalText": "차단\n학습 기간 보호",
      "lineHeight": 1.25
    },
    {
      "id": "text-approve",
      "type": "text",
      "x": 1830.5,
      "y": 402.0,
      "width": 139.0,
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
      "seed": 1041752723,
      "version": 1,
      "versionNonce": 1210142476,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1760000000000,
      "link": null,
      "locked": false,
      "text": "사람 승인 →\n반영 · 재조회 검증",
      "fontSize": 20,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 41.4,
      "containerId": "node-approve",
      "originalText": "사람 승인 →\n반영 · 재조회 검증",
      "lineHeight": 1.25
    },
    {
      "id": "title",
      "type": "text",
      "x": 0,
      "y": 0.0,
      "width": 285.0,
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
      "text": "메타형 위닝 광고 스케일업",
      "fontSize": 28,
      "fontFamily": 2,
      "textAlign": "left",
      "verticalAlign": "top",
      "baseline": 22.96,
      "containerId": null,
      "originalText": "메타형 위닝 광고 스케일업",
      "lineHeight": 1.25
    },
    {
      "id": "subtitle",
      "type": "text",
      "x": 0,
      "y": 41.0,
      "width": 646.0,
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
      "text": "지표 조건 → 증액·중지 후보 → 학습 기간을 지키는 안전장치 → 사람 승인 (기본 규칙 meta.yaml 기준)",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "left",
      "verticalAlign": "top",
      "baseline": 13.12,
      "containerId": null,
      "originalText": "지표 조건 → 증액·중지 후보 → 학습 기간을 지키는 안전장치 → 사람 승인 (기본 규칙 meta.yaml 기준)",
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
예 ^label-edge-win-up-2
예 ^label-edge-lose-pause-3
위반 ^label-edge-guard-block-7
통과 ^label-edge-guard-approve-8
소재 단위 일별 실적
→ 세트 단위로 합산 ^text-collect
위닝 조건?
ROAS ≥ 350%
전환 ≥ 20건 · 상위 절반 ^text-win
소재 조건?
CTR -30%↓ & 빈도 3.5↑
또는 ROAS < 70% ^text-lose
세트 예산
+20% 후보 ^text-up
소재 중지 후보 ^text-pause
조정안
근거 문장 자동 생성 ^text-cand
안전장치
변경 폭 ≤ 20%
쿨다운 3일 · 하루 6건 ^text-guard
차단
학습 기간 보호 ^text-block
사람 승인 →
반영 · 재조회 검증 ^text-approve
메타형 위닝 광고 스케일업 ^title
지표 조건 → 증액·중지 후보 → 학습 기간을 지키는 안전장치 → 사람 승인 (기본 규칙 meta.yaml 기준) ^subtitle
%%
