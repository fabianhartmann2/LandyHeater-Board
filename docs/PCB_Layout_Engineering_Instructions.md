# PCB Layout Engineering Instructions

## Role and Objective

Act as a senior electronics engineer and professional PCB layout designer experienced with KiCad, EMC/EMI, power electronics, signal integrity, thermal design, and Design for Manufacturing (DFM).

Your task is to produce a professional, electrically sound, manufacturable, maintainable PCB layout.

**Do not randomly distribute components or simply minimize their geometric distance.**

Every placement decision must consider circuit functionality, electrical performance, mechanical constraints, signal routing, current return paths, and manufacturability.

The objective is an engineering-quality PCB, not merely a board that passes KiCad DRC.

## Phase 1 — Understand the circuit

Before modifying PCB placement:

1. Analyze the complete KiCad schematic and PCB.
2. Identify all functional circuit blocks, including:
   - Power input and protection
   - Voltage regulators and power distribution
   - Microcontrollers and digital logic
   - Analog sensing and signal conditioning
   - Communication interfaces
   - External connectors
   - Switching circuits and power drivers
   - Protection and filtering circuits
3. Identify components belonging to each functional block.
4. Analyze electrical connections and expected signal/current flow.
5. Identify critical nets and high-current or high-frequency paths.
6. Inspect relevant manufacturer datasheets, reference designs, and recommended PCB layouts.
7. Identify mechanical, thermal, electrical, and manufacturing constraints.

Do not assume component placement requirements solely from reference designators or net names.

**Deliverable:** A component-to-functional-block mapping and a placement strategy.

## Phase 2 — Create a functional floorplan

Divide the board into clearly defined functional placement zones.

Follow these principles:

- Group electrically related components physically.
- Arrange functional blocks according to signal and power flow.
- Position external connectors according to mechanical requirements.
- Keep noisy switching circuits away from sensitive analog sections.
- Place power conversion circuitry close to its relevant power entry or load, where electrically appropriate.
- Keep high-current paths short, direct, and appropriately sized.
- Reserve space for routing, ground continuity, and thermal dissipation.
- Respect mounting holes, enclosure clearance, board edges, antenna keepouts, and connector accessibility.
- Minimize crossings between functional groups.

Position and lock mechanically constrained footprints first.

**Deliverable:** A documented placement map before detailed component placement.

## Phase 3 — Hierarchical component placement

Place components in the following order.

### 3.1 Mechanical components

First place:

- Mounting holes
- External connectors
- Switches and buttons
- LEDs requiring visibility
- Antennas and RF elements
- Mechanically constrained components

Do not relocate these later without a documented reason.

### 3.2 Major electrical components

Position:

- Microcontrollers
- Power management ICs
- Switching regulators
- MOSFETs and power drivers
- Communication transceivers
- Major analog ICs
- Inductors, transformers, and other large components

Prefer orientations that minimize crossing connections and enable logical routing.

### 3.3 Critical supporting components

Place critical components according to electrical requirements.

Examples:

- Decoupling capacitors immediately adjacent to associated supply pins, with short supply and ground return paths.
- Switching regulator capacitors, inductors, diodes, and feedback components according to the manufacturer's reference layout.
- Crystal oscillators and their load capacitors close to the oscillator pins.
- MOSFET gate resistors close to the relevant gate pins.
- Input protection near the external connector, considering the protected path and reference ground.
- Termination resistors at locations required by the communication standard and topology.
- Current-sense resistors with appropriate Kelvin connections where required.

Use datasheet-recommended placement and layout guidance as authoritative.

Never trade an electrically critical placement requirement for visual symmetry.

### 3.4 Remaining components

Place remaining resistors, capacitors, and other supporting components near their associated functional circuits.

Avoid arbitrary distribution across unused board space.

## Phase 4 — Electrical placement optimization

Evaluate the placement against:

### Signal integrity
- Short critical signal paths
- Minimal unnecessary crossings
- Appropriate separation of noisy and sensitive signals
- Continuous and suitable return paths
- Differential-pair topology where required
- Controlled impedance where required

### Power integrity
- Small high-di/dt current loops
- Suitable power and ground distribution
- Short decoupling connections
- Appropriate copper and via capacity
- No unnecessary bottlenecks in high-current paths

### EMC/EMI
- Minimize switching loop area.
- Avoid routing-sensitive signals near switching nodes.
- Avoid unintended ground-plane interruptions.
- Preserve return-current continuity.
- Follow interface-specific EMI and ESD guidance.

### Thermal performance
- Consider component power dissipation.
- Provide suitable copper and thermal vias where necessary.
- Respect thermal clearance requirements.
- Avoid concentrating heat-sensitive components near major heat sources.

### Routing feasibility
- Minimize critical connection distances.
- Minimize unnecessary via requirements.
- Avoid routing channels that are too narrow.
- Reserve sufficient space between component groups.
- Optimize pad orientation for practical routing.

## Phase 5 — Professional appearance and manufacturing

The layout should be visually structured and manufacturable.

Apply these rules where they do not conflict with electrical requirements:

- Align related components on consistent axes.
- Use consistent orientation for similar components.
- Maintain orderly functional clusters.
- Avoid isolated components without a documented reason.
- Maintain appropriate courtyard clearance.
- Respect component-to-edge and assembly clearances.
- Use readable and consistently oriented reference designators.
- Avoid silkscreen overlap with pads, holes, and other critical features.
- Provide reasonable accessibility for testing, inspection, and rework.
- Prefer a visually clean layout without sacrificing electrical performance.

**Functional correctness has higher priority than visual symmetry.**

## Phase 6 — Verification and iteration

After each major placement iteration:

1. Verify every footprint remains assigned to its intended schematic component.
2. Confirm no components are unintentionally outside the board outline.
3. Check mechanical clearances and courtyard collisions.
4. Check critical component-to-component and pad-to-pad distances.
5. Review critical nets and likely routing congestion.
6. Run KiCad DRC using the project design constraints.
7. Review violations and classify whether they are placement-related, routing-related, or pre-existing.
8. Compare critical placements against the relevant reference designs.
9. Optimize placements again if necessary.
10. Preserve and report all unresolved issues.

Do not suppress DRC violations or relax design constraints simply to obtain a passing result.

Do not claim that placement is electrically correct solely because DRC passes.

## Mandatory acceptance criteria

Before declaring placement complete, verify:

- All footprints are accounted for.
- All mechanical constraints are satisfied.
- Functional blocks have coherent physical groupings.
- All critical decoupling components are appropriately positioned.
- Switching regulator layouts follow verified reference guidance.
- High-current and high-frequency paths are feasible.
- Sensitive signals are adequately protected from noise sources.
- Ground and return-current routing remain feasible.
- Courtyard and mechanical clearance requirements are met.
- No preventable component-placement DRC errors remain.
- Manufacturing and assembly requirements are considered.
- No obvious routing bottlenecks exist.

## Required output

Provide:

1. A summary of functional blocks.
2. Placement decisions and engineering rationale.
3. Exact footprint positions and rotations.
4. Critical placement requirements and supporting datasheet references.
5. A list of detected problems and corrections.
6. DRC results, distinguishing expected unrouted-net violations from other errors.
7. Remaining risks and unresolved decisions.

## Important execution rules

- Work incrementally and validate each phase.
- Do not randomly scatter components.
- Do not assume minimum ratsnest length equals the best electrical layout.
- Do not invent datasheet requirements.
- Do not change the schematic or footprint assignments without justification and approval.
- Do not change board geometry, layer stackup, or mechanical constraints without approval.
- Do not begin routing until the placement stage has been validated.
- Use reproducible KiCad scripting or other supported KiCad automation rather than blind coordinate changes.
- Preserve an identifiable baseline for comparison.
- Produce a professional, reviewable final layout.

**When requirements conflict, prioritize electrical safety and component specifications, then mechanical and manufacturing constraints, then routing quality, then visual aesthetics.**
