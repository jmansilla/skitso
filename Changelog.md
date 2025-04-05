# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1.13] - 2025-04-04

### Added

  - Configurable file format for scene frames

## [0.1.11] - 2025-03-06

### Added

  - Aligment objects are comparable, and also have a native conversion to string

### Fixed

  - Fixed movement on to_edge when needing to move right and/or low edges

## [0.1.10] - 2025-02-25

### Added

  - Text has configurable params, easier to subclass


## [0.1.9] - 2025-02-24

### Changed

  - Removed shape DeadArrow. It's code that its for user space, and not library
  - BaseImgElem class has now a (default:0) z_index attribute, linters not complaining any more

## [0.1.8] - 2025-02-20

### Added

  - If children of container have z_index attribute, its used for drawing in such order

### Fixed
  - Deduplicated code from Scene and Container

## [0.1.4] - 2025-02-13

### Changed

  - Allowing pillow version from 10.4 and above (instead of starting at 11.0)
  - Scene folder path easier to customize

## [0.1.2] - 2025-01-16

### Added

  - Pencil has image attribute to enable pasting images
  - Antialising disabled by default (configurable to scene objects)

### Fixed

  - DeadArrow working properly. Now inherits from Container.
  - Removed dead code (DIRECT attr)
  - Scenes located at 0,0

## [0.1.0] - 2024-11-10

Initial version.

### Added
  - Basic shapes
  - Scene Generator
