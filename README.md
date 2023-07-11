# Module Progress Dashboard
>
> Authors: Ranjit Sundaramurthi

## About

An open-source Dashboard to visualize the student progress on courses. The primary users are administrators who manage large non-academic courses. The stakeholders for the Dashboard are admins/instructors while the subjects are the students enrolled in courses. Each instructor might create multiple courses. Each course in turn has several modules which are in turn comprised of items. These items may be of the type Page, Discussion, Video or Quiz etc. A module is said to be completed for a specific student when he/she has completed the designated requirements of items underneath it. Note that depending on the item type, the requirement may be different and often the item might be optional.

The Dashboard provides the users the following insights:

* The progress of the students at course level.
* Each course is comprised of multiple modules. The Dashboard provides the user an understanding as to which module are the students currently working on. The progress of the students on the modules may also enable the instructors to decide whether the course should be designed in a sequential fashion or made flexible.
* Completion percentage of a module amongst all students enrolled in the course.
* Completion percentage of a student across different modules in the course.
* Completion percentage of a student across different items in a module.
* Completion percentage of an item amongst all students in a module.

## Layout

The Dashboard is comprised of two tabs to segment into two distinct sections. The first tab provides the user with Course specific information at the module hierarchy level. The second tab provides the user with Course and Module specific information at the item hierarch level.

The top of the Dashboard has two overall filters: by Course and by Student. By default, the first Course (alphabetically) and All students are selected.

![Dashboard_tab1](/img/dashboard_pg1.PNG)
The sidebar on the left enables the user to single, all or multiple modules that are present within the selected course.

For the selecte modules, the visualization are showcases a lineplot of the student percentage completion over time. It also shows a stacked barplot of the statuses: 'locked', 'unlocked', 'started' and 'completed'. The bottom half presents a datable with student counts. A box plot presenting the time to complete each module is planned to provide insights on modules that might be time consuming/challenging.

Note that when a specific Student is selected in the overall filter, the visualization are dynamically changes to a scatter plot (as student percentage completion is longer a reasonable computation). The box plot is planned to be retained to show completion time as a separate scatter plot as well.

![Dashboard_tab2](/img/dashboard_pg2.PNG)
The second tab of the Dashboard contains a different sidebar. This sidebar compels the user to select a specific module within the already selected combination of course and student filters. The selection of the module, activates and populates the items checklist. By default 'All' items are selected. The user is allowed to select 'All', single or multiple items.

The visualization area showcases a barplot of the count of types of items under the selected module. Specifically for items that are mandatory, the student percentage completion is depicted as a stacked barplot. he bottom half presents a datable with student counts. Since items completion are not tracked by a timestamp in the dataset, average completion time of items cannot be visualized.

As before, when a specific Student is selected in the overall filter, the visualization dynamically changes to a scatter plot (as student percentage completion is longer a reasonable computation).

The bottom of the Dashboard contains attributions, source, assumptions and summary.

## Data-Source

Canvas API through module progress.
(OR)
Develop a javascript for Tampermonkey to extract data through the Canvas API.

## Documentation

Capture learnings, detailed documentation on development cycle.

## Usage

Setup instructions, running instrutions, data privacy measures, .gitignore rules
