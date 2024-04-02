# AI-Project-Hamumlezet
Personalized course planning system. Helping students to reach graduation as efficiently as possible 
<p align="center">
<img src="/Images/Logo.png" width="250">
</p>

## Introduction
The Technion – Israel Institute of Technology is a leading public research university in Haifa, Israel, specializing in engineering and precise sciences. This project, known as "המומלצת המומלצת" (Technion Study Path Recommender), addresses the challenge students face in personalizing their semester and degree schedules. Despite the Technion providing a recommended schedule, students often encounter difficulties tailoring it to their preferences and needs. This project introduces an advanced recommendation system to assist students in crafting a personalized academic path.

## Problem
Students frequently seek a more personalized approach to course planning, feeling that a generic recommended system might not be the best fit. Constructing an optimal semester timetable and planning the path to degree completion becomes challenging due to complex requirements, prerequisites, and potential academic irregularities. The order of taking courses is crucial but is often overlooked, resulting in delayed graduation.

## Solution
Introducing an AI-based recommendation system that guides students toward the most personalized and efficient path to degree completion. The system prioritizes optimal academic success and the fastest route to graduation.

## System Structure
<p align="center">
<img src="/Images/Diagram.png" width="500">
</p>

### Main Components
- **Course:** Represents a course, encompassing details such as name, credits, prerequisites, and schedule.
- **State:** Reflects the student's academic status within the study program.
- **Student:** Captures the student's input profile.

### Key Parts
- **Data Infrastructure:** Gathers and organizes essential data for program execution.
- **Course Graph:** Models courses and their relationships in a Directed Acyclic Graph (DAG).
- **Options Graph:** Constructs all legal paths to degree completion.
- **Search:** Utilizes the A* algorithm for optimal pathfinding, incorporating various heuristics based on student preferences.

## Technologies Used
The system is implemented in Python, leveraging the following libraries:
- **Beautiful Soup:** Extracts data from HTML and XML files.
- **Networkx:** Manages graph structures for efficient handling of course relationships.
- **Pandas, Matplotlib, Seaborn:** Experiments analysis and visualizations

