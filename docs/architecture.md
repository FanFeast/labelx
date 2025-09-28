# Architecture (overview)

Annox converts datasets between formats via a versioned intermediate schema. Adapters import/export the schema. IO and parallelism modules centralize performance-sensitive paths. Optional Rust accelerators optimize hotspots.

