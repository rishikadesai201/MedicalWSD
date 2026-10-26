"""Human-authored synthetic teaching contexts; never copied from a corpus."""

# Each family is its own split unit. Its two surface realizations share one
# group_id so no paraphrase of a family can appear on both sides of a split.
TEMPLATE_FAMILIES = [
    # PE: Pulmonary embolism
    {"abbr": "PE", "sense": "Pulmonary embolism", "family": "pe_vte_1", "difficulty": "clear", "texts": [
        "The imaging summary marks PE after describing a clot in a branch of a lung artery.",
        "A lung-vessel clot is the central clue in the teaching vignette labeled PE."]},
    {"abbr": "PE", "sense": "Pulmonary embolism", "family": "pe_vte_2", "difficulty": "clear", "texts": [
        "The discussion of venous thrombosis records PE in the assessment section.",
        "After a leg-vein clot is mentioned, the vignette turns to PE and the lungs."]},
    {"abbr": "PE", "sense": "Pulmonary embolism", "family": "pe_vte_3", "difficulty": "clear", "texts": [
        "Chest CT and a D-dimer result appear in the teaching example about PE.",
        "The workup summary places PE beside the imaging of a pulmonary arterial blockage."]},
    {"abbr": "PE", "sense": "Pulmonary embolism", "family": "pe_vte_4", "difficulty": "clear", "texts": [
        "The case discussion links PE with a clot that traveled from a deep leg vein.",
        "A sudden breathing complaint follows a venous clot in the vignette marked PE."]},
    {"abbr": "PE", "sense": "Pulmonary embolism", "family": "pe_vte_5", "difficulty": "moderate", "texts": [
        "The instructor reviews anticoagulation after the PE section on lung-vessel clots.",
        "The teaching note groups venous thromboembolism and PE under vascular findings."]},
    {"abbr": "PE", "sense": "Pulmonary embolism", "family": "pe_vte_6", "difficulty": "moderate", "texts": [
        "A pulmonary artery filling defect is discussed; the target abbreviation is PE.",
        "The assessment lists PE, with the surrounding text describing an embolic lung-vessel event."]},
    {"abbr": "PE", "sense": "Pulmonary embolism", "family": "pe_vte_7", "difficulty": "moderate", "texts": [
        "The teaching case considers a lung clot after prolonged immobility and labels it PE.",
        "In the PE vignette, the notes connect a venous source with an obstruction in the lungs."]},
    {"abbr": "PE", "sense": "Pulmonary embolism", "family": "pe_vte_8", "difficulty": "moderate", "texts": [
        "CT pulmonary angiography is reviewed in a vignette whose target term is PE.",
        "The review of a pulmonary arterial clot places PE in the diagnostic summary."]},
    {"abbr": "PE", "sense": "Pulmonary embolism", "family": "pe_vte_9", "difficulty": "moderate", "texts": [
        "The lung-vessel blockage example places PE in the assessment after venous clot findings.",
        "The case review discusses embolic material reaching the pulmonary circulation; it labels the event PE."]},
    {"abbr": "PE", "sense": "Pulmonary embolism", "family": "pe_vte_10", "difficulty": "moderate", "texts": [
        "A blood-clot migration vignette describes PE in the lung circulation.",
        "The PE discussion follows the note about a deep-vein thrombus and chest imaging."]},
    {"abbr": "PE", "sense": "Pulmonary embolism", "family": "pe_vte_11", "difficulty": "moderate", "texts": [
        "The case labels PE after describing an embolic obstruction of a pulmonary vessel.",
        "The review links venous thrombosis, lung perfusion imaging, and the abbreviation PE."]},

    # PE: Physical examination
    {"abbr": "PE", "sense": "Physical examination", "family": "pe_exam_1", "difficulty": "clear", "texts": [
        "The oncology abstract has a PE heading followed by skin and lymph-node observations.",
        "The staging summary places body-inspection findings under PE, before the imaging section."]},
    {"abbr": "PE", "sense": "Physical examination", "family": "pe_exam_2", "difficulty": "clear", "texts": [
        "During PE, the examiner records palpation findings and general appearance.",
        "The note documents auscultation and inspection in the section marked PE."]},
    {"abbr": "PE", "sense": "Physical examination", "family": "pe_exam_3", "difficulty": "clear", "texts": [
        "The diagnostic workup lists PE before laboratory and imaging sections.",
        "A report separates PE findings from blood tests and radiology results."]},
    {"abbr": "PE", "sense": "Physical examination", "family": "pe_exam_4", "difficulty": "clear", "texts": [
        "The registrar summarizes body inspection and palpation beneath PE.",
        "The clinician's PE entry records the appearance of the skin and palpable nodes."]},
    {"abbr": "PE", "sense": "Physical examination", "family": "pe_exam_5", "difficulty": "moderate", "texts": [
        "The note says PE was documented, then lists auscultation findings.",
        "Under PE, the examination template records chest sounds and abdominal palpation."]},
    {"abbr": "PE", "sense": "Physical examination", "family": "pe_exam_6", "difficulty": "moderate", "texts": [
        "A staging vignette places clinical examination findings in the PE section.",
        "Inspection and palpation results are grouped together under the heading PE."]},
    {"abbr": "PE", "sense": "Physical examination", "family": "pe_exam_7", "difficulty": "moderate", "texts": [
        "The abstract separates PE findings from the radiology report.",
        "Under PE, the clinician documents inspection and palpation results before tests are listed."]},
    {"abbr": "PE", "sense": "Physical examination", "family": "pe_exam_8", "difficulty": "moderate", "texts": [
        "A diagnostic summary groups physical findings and general inspection beneath PE.",
        "The record's PE section comes before laboratory investigations and contains examination observations."]},
    {"abbr": "PE", "sense": "Physical examination", "family": "pe_exam_9", "difficulty": "moderate", "texts": [
        "The staging exercise uses PE for the clinician's inspection of the body.",
        "The physician records palpation and visible findings under PE in the sample abstract."]},
    {"abbr": "PE", "sense": "Physical examination", "family": "pe_exam_10", "difficulty": "moderate", "texts": [
        "The clinical worksheet puts auscultation notes in the PE subsection.",
        "A reviewer finds skin, node, and general-appearance observations beneath PE."]},
    {"abbr": "PE", "sense": "Physical examination", "family": "pe_exam_11", "difficulty": "moderate", "texts": [
        "The encounter summary places PE between the review of systems and ordered tests.",
        "The PE entry contains the examiner's observations rather than imaging interpretations."]},

    # PA: Pulmonary artery
    {"abbr": "PA", "sense": "Pulmonary artery", "family": "pa_vessel_1", "difficulty": "clear", "texts": [
        "The echo report gives a PA pressure estimate and describes right-ventricular flow.",
        "The cardiology teaching diagram shows blood leaving the right ventricle through the PA."]},
    {"abbr": "PA", "sense": "Pulmonary artery", "family": "pa_vessel_2", "difficulty": "clear", "texts": [
        "A catheter is advanced into the PA during the hemodynamics teaching scenario.",
        "The catheterization note compares pressure in the PA with right-sided heart measurements."]},
    {"abbr": "PA", "sense": "Pulmonary artery", "family": "pa_vessel_3", "difficulty": "clear", "texts": [
        "The anatomy figure traces blood from the right ventricle into the PA.",
        "The vessel labeled PA carries blood from the heart toward the lungs."]},
    {"abbr": "PA", "sense": "Pulmonary artery", "family": "pa_vessel_4", "difficulty": "clear", "texts": [
        "The cardiology note compares PA pressure with systemic arterial pressure.",
        "A pressure measurement in the PA is included in the right-heart study summary."]},
    {"abbr": "PA", "sense": "Pulmonary artery", "family": "pa_vessel_5", "difficulty": "moderate", "texts": [
        "The diagram labels the vessel beside the right ventricle as PA.",
        "The discussion of pulmonary circulation identifies the PA near the heart's right side."]},
    {"abbr": "PA", "sense": "Pulmonary artery", "family": "pa_vessel_6", "difficulty": "moderate", "texts": [
        "The echo teaching note reports PA pressure during the assessment of pulmonary flow.",
        "A right-heart catheter records a pressure value for the PA in the example."]},
    {"abbr": "PA", "sense": "Pulmonary artery", "family": "pa_vessel_7", "difficulty": "moderate", "texts": [
        "The anatomy review places the PA between the right ventricle and lung circulation.",
        "The vascular structure marked PA is discussed alongside pulmonary blood flow."]},
    {"abbr": "PA", "sense": "Pulmonary artery", "family": "pa_vessel_8", "difficulty": "moderate", "texts": [
        "A pressure tracing from the PA appears in the hemodynamic worksheet.",
        "The report discusses a catheter measurement from the vessel leading to the lungs, labeled PA."]},
    {"abbr": "PA", "sense": "Pulmonary artery", "family": "pa_vessel_9", "difficulty": "moderate", "texts": [
        "The cardiology slide labels the right-ventricle outflow vessel PA.",
        "The pulmonary circulation diagram marks PA beside the branching lung vessels."]},
    {"abbr": "PA", "sense": "Pulmonary artery", "family": "pa_vessel_10", "difficulty": "moderate", "texts": [
        "The echo worksheet records an estimated PA systolic pressure.",
        "The right-heart study describes PA pressure and flow toward both lungs."]},
    {"abbr": "PA", "sense": "Pulmonary artery", "family": "pa_vessel_11", "difficulty": "moderate", "texts": [
        "A teaching note follows blood from the right ventricle into the vessel labeled PA.",
        "The PA is shown as part of pulmonary circulation in the anatomy review."]},

    # PA: Physician assistant
    {"abbr": "PA", "sense": "Physician assistant", "family": "pa_role_1", "difficulty": "clear", "texts": [
        "A PA joined the care team and completed the intake interview.",
        "The staffing note lists the PA alongside the supervising physician."]},
    {"abbr": "PA", "sense": "Physician assistant", "family": "pa_role_2", "difficulty": "clear", "texts": [
        "The PA documented the visit and relayed the plan to the physician.",
        "A PA role appears in the clinic roster beside nursing and physician staff."]},
    {"abbr": "PA", "sense": "Physician assistant", "family": "pa_role_3", "difficulty": "clear", "texts": [
        "The patient met with a PA before the physician reviewed the note.",
        "A PA conducted the visit while the supervising clinician remained available."]},
    {"abbr": "PA", "sense": "Physician assistant", "family": "pa_role_4", "difficulty": "clear", "texts": [
        "The clinic note attributes the history-taking to the PA.",
        "The PA is named as a member of the outpatient care team in the vignette."]},
    {"abbr": "PA", "sense": "Physician assistant", "family": "pa_role_5", "difficulty": "moderate", "texts": [
        "The staffing schedule assigns the PA to the afternoon clinic session.",
        "A PA and a physician are listed as the clinicians for the teaching encounter."]},
    {"abbr": "PA", "sense": "Physician assistant", "family": "pa_role_6", "difficulty": "moderate", "texts": [
        "The PA reviewed the intake history with the attending physician.",
        "The encounter summary says the PA recorded the interview before handoff."]},
    {"abbr": "PA", "sense": "Physician assistant", "family": "pa_role_7", "difficulty": "moderate", "texts": [
        "The clinical team roster identifies the PA as a care provider.",
        "The note is signed by the PA, who coordinated the visit with the physician."]},
    {"abbr": "PA", "sense": "Physician assistant", "family": "pa_role_8", "difficulty": "moderate", "texts": [
        "A PA is assigned to the clinic team for the simulated outpatient visit.",
        "The physician assistant role is represented by PA in the staffing worksheet."]},
    {"abbr": "PA", "sense": "Physician assistant", "family": "pa_role_9", "difficulty": "moderate", "texts": [
        "The patient-facing role in the vignette is a PA working with a physician.",
        "The PA documented the conversation and then consulted the supervising clinician."]},
    {"abbr": "PA", "sense": "Physician assistant", "family": "pa_role_10", "difficulty": "moderate", "texts": [
        "The outpatient schedule places the PA in the same team as the physician.",
        "A PA conducts the intake in the staffing example before the doctor joins the visit."]},
    {"abbr": "PA", "sense": "Physician assistant", "family": "pa_role_11", "difficulty": "moderate", "texts": [
        "The clinician line lists a PA as the person who obtained the history.",
        "The role marked PA is discussed with other members of the care team."]},

    # AP: Anteroposterior
    {"abbr": "AP", "sense": "Anteroposterior", "family": "ap_projection_1", "difficulty": "clear", "texts": [
        "The radiograph is labeled AP, and the beam direction is described from front to back.",
        "The image uses an AP projection while the subject is positioned supine."]},
    {"abbr": "AP", "sense": "Anteroposterior", "family": "ap_projection_2", "difficulty": "clear", "texts": [
        "The report compares AP and lateral views of the thorax.",
        "The radiology worksheet identifies the front-to-back image as AP."]},
    {"abbr": "AP", "sense": "Anteroposterior", "family": "ap_projection_3", "difficulty": "clear", "texts": [
        "The positioning note identifies the AP orientation on the portable film.",
        "The acquisition record marks the chest projection AP rather than lateral."]},
    {"abbr": "AP", "sense": "Anteroposterior", "family": "ap_projection_4", "difficulty": "clear", "texts": [
        "The radiology slide labels the front-to-back projection AP.",
        "An AP view is discussed beside a lateral radiograph in the teaching set."]},
    {"abbr": "AP", "sense": "Anteroposterior", "family": "ap_projection_5", "difficulty": "moderate", "texts": [
        "The portable image is marked AP in the acquisition note.",
        "The beam enters from the anterior side and exits posteriorly in the AP view."]},
    {"abbr": "AP", "sense": "Anteroposterior", "family": "ap_projection_6", "difficulty": "moderate", "texts": [
        "The report lists an AP projection and a second lateral projection.",
        "The film is described as AP because the imaging path runs front to back."]},
    {"abbr": "AP", "sense": "Anteroposterior", "family": "ap_projection_7", "difficulty": "moderate", "texts": [
        "The image orientation is recorded as AP in the radiographic worksheet.",
        "The chest film is taken in a front-to-back direction and labeled AP."]},
    {"abbr": "AP", "sense": "Anteroposterior", "family": "ap_projection_8", "difficulty": "moderate", "texts": [
        "A radiograph marked AP is contrasted with the lateral image in the report.",
        "The positioning summary describes an anterior-to-posterior beam for the AP view."]},
    {"abbr": "AP", "sense": "Anteroposterior", "family": "ap_projection_9", "difficulty": "moderate", "texts": [
        "The radiology teaching file places the AP label on the frontal projection.",
        "The film's projection direction is from the front toward the back, noted as AP."]},
    {"abbr": "AP", "sense": "Anteroposterior", "family": "ap_projection_10", "difficulty": "moderate", "texts": [
        "The acquisition note records an AP chest image with the beam passing front to back.",
        "The image is AP, while the companion view is obtained from the side."]},
    {"abbr": "AP", "sense": "Anteroposterior", "family": "ap_projection_11", "difficulty": "moderate", "texts": [
        "The technician's worksheet labels the anteroposterior projection AP.",
        "The radiology report distinguishes the AP image from the lateral view."]},

    # AP: Anterior pituitary
    {"abbr": "AP", "sense": "Anterior pituitary", "family": "ap_gland_1", "difficulty": "clear", "texts": [
        "The endocrine diagram labels the AP beside the hypothalamus and hormone-producing cells.",
        "The pituitary-axis chart identifies the AP as the glandular lobe in the lesson."]},
    {"abbr": "AP", "sense": "Anterior pituitary", "family": "ap_gland_2", "difficulty": "clear", "texts": [
        "ACTH is discussed in the endocrine section about the AP.",
        "The lesson connects the AP with TSH secretion and endocrine feedback."]},
    {"abbr": "AP", "sense": "Anterior pituitary", "family": "ap_gland_3", "difficulty": "clear", "texts": [
        "The AP is marked on the diagram next to the pituitary stalk.",
        "The endocrine worksheet places the AP in the glandular region below the hypothalamus."]},
    {"abbr": "AP", "sense": "Anterior pituitary", "family": "ap_gland_4", "difficulty": "clear", "texts": [
        "The endocrine review labels the hormone-releasing pituitary lobe AP.",
        "A pituitary-axis chart shows the AP upstream of several target glands."]},
    {"abbr": "AP", "sense": "Anterior pituitary", "family": "ap_gland_5", "difficulty": "moderate", "texts": [
        "The lesson describes ACTH and TSH in the section marked AP.",
        "The endocrine diagram places AP beside the pituitary stalk and hormone pathways."]},
    {"abbr": "AP", "sense": "Anterior pituitary", "family": "ap_gland_6", "difficulty": "moderate", "texts": [
        "The glandular lobe shown in the pituitary feedback diagram is labeled AP.",
        "In the endocrine review, AP appears near the hypothalamus and target-gland arrows."]},
    {"abbr": "AP", "sense": "Anterior pituitary", "family": "ap_gland_7", "difficulty": "moderate", "texts": [
        "The hormone chart places ACTH beneath the heading AP.",
        "The endocrine worksheet uses AP beside TSH and other pituitary outputs."]},
    {"abbr": "AP", "sense": "Anterior pituitary", "family": "ap_gland_8", "difficulty": "moderate", "texts": [
        "The pituitary diagram marks AP on the lobe connected with endocrine feedback.",
        "The AP is discussed with hormone secretion in the glandular-pituitary lesson."]},
    {"abbr": "AP", "sense": "Anterior pituitary", "family": "ap_gland_9", "difficulty": "moderate", "texts": [
        "The endocrine figure labels the pituitary lobe near the stalk as AP.",
        "The hormone pathway review places AP above the target-gland response boxes."]},
    {"abbr": "AP", "sense": "Anterior pituitary", "family": "ap_gland_10", "difficulty": "moderate", "texts": [
        "A teaching chart links AP with ACTH release and pituitary feedback.",
        "The endocrine note identifies AP in the section on pituitary hormones."]},
    {"abbr": "AP", "sense": "Anterior pituitary", "family": "ap_gland_11", "difficulty": "moderate", "texts": [
        "The pituitary-axis review places AP beside the hypothalamus and endocrine targets.",
        "The diagram's AP label points to the pituitary tissue associated with hormone outputs."]},
]
