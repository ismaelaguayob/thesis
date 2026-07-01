

Universidad de Chile

Facultad de Ciencias Sociales

Departamento de Sociología  
Carrera de Sociología

Memoria para optar al título profesional de Sociólogo/a

**Resiliencia de la capitalización individual: Mapeando redes discursivas de justicia social en el debate previsional chileno**

**AUTOR/A: Ismael Aguayo**

**PROFESOR GUÍA: Juan Carlos Castillo**

**FECHA: 30 de junio de 2026**

Memoria desarrollada en el marco del proyecto de Fondecyt Nº 1250518 y el Centro Nacional de Inteligencia Artificial CENIA FB210017, Financiamiento Basal ANID

[**Abstract	4**](#abstract)

[**Introducción	5**](#introducción)

[**1\. La dimensión moral y normativa en el debate previsional	8**](#1.-la-dimensión-moral-y-normativa-en-el-debate-previsional)

[1.1. Justicia de mercado vs. Justicia política: Los mercados como economías morales	8](#1.1.-justicia-de-mercado-vs.-justicia-política:-los-mercados-como-economías-morales)

[1.2. La condicionalidad de la seguridad social en la vejez	9](#1.2.-la-condicionalidad-de-la-seguridad-social-en-la-vejez)

[**2\. Resiliencia institucional y legitimación discursiva: el rol de las ideas	11**](#2.-resiliencia-institucional-y-legitimación-discursiva:-el-rol-de-las-ideas)

[2.1. Robustez neoliberal y el rol de las ideas	11](#2.1.-robustez-neoliberal-y-el-rol-de-las-ideas)

[2.2 El discurso como poder y hegemonía	13](#2.2-el-discurso-como-poder-y-hegemonía)

[2.3 Estrategias de legitimación y los discursos tecnocráticos	15](#2.3-estrategias-de-legitimación-y-los-discursos-tecnocráticos)

[**3\. El debate previsional chileno: la conformación de tres coaliciones	16**](#3.-el-debate-previsional-chileno:-la-conformación-de-tres-coaliciones)

[**4\. Metodología	20**](#4.-metodología)

[4.1 Datos	20](#4.1-datos)

[4.2 Variables	21](#4.2-variables)

[4.3 Estrategia de análisis	22](#4.3-estrategia-de-análisis)

[4.3.1 Estrategia de codificación y validación	22](#4.3.1-estrategia-de-codificación-y-validación)

[4.3.2 Análisis descriptivo y modelamiento de patrones discursivos	23](#4.3.2-análisis-descriptivo-y-modelamiento-de-patrones-discursivos)

[**Referencias	26**](#referencias)

## **Abstract** {#abstract}

El sistema de pensiones de capitalización individual en Chile ha persistido institucionalmente a pesar de su profunda crisis de legitimidad, la alta conflictividad social y los sucesivos intentos de transformación estructural. En este contexto, la presente investigación examina cómo las diferentes concepciones de justicia social son justificadas y operan en el discurso político para defender o disputar las bases normativas de este modelo. El argumento central del estudio postula que la resiliencia de la capitalización individual depende, en gran medida, de su capacidad institucional para ordenar discursivamente los límites y alcances del debate normativo. Para explorar esto, se hipotetiza que el debate se estructura en tres coaliciones discursivas principales, ancladas en visiones divergentes sobre la justicia de mercado y la justicia política. Se espera que estas coaliciones movilicen repertorios estratégicos diferenciados y criterios concretos de merecimiento (CARIN) , derivando en una convergencia pragmática donde las lógicas de solidaridad quedan subordinadas a la primacía de la propiedad individual y el mérito. Metodológicamente, la investigación aplica el Análisis de Redes Discursivas (DNA) , articulando una codificación cualitativa asistida por Modelos de Lenguaje Grande (LLM), rigurosa validación manual y modelos estadísticos multinivel de clasificación cruzada. El análisis se basa en un corpus exhaustivo compuesto por las transcripciones del debate legislativo de la Ley N° 21.735 (2022-2025). Este conjunto de datos abarca un N total de 92 sesiones documentadas, provenientes tanto de discusiones en sala como de comisiones técnicas (Trabajo y Previsión Social, y Hacienda) en la Cámara de Diputados y el Senado.

**Palabras clave:** Capitalización individual, justicia social, merecimiento, institucionalismo discursivo, análisis de redes discursivas.

## **Introducción** {#introducción}

Los sistemas de pensiones constituyen una de las instituciones de protección social más determinantes en el ciclo de vida, al organizar la distribución de recursos en la vejez y al proteger a las personas frente a dificultades (Ebbinghaus & Wiß, 2024). Desde la sociología de la justicia, las políticas sociales cristalizan concepciones normativas sobre qué se considera una distribución legítima del bienestar, y esas concepciones se vuelven especialmente visibles cuando una reforma cuestiona el equilibrio entre Estado, mercado y familia (Esping-Andersen, 1990; Liebig & Sauer, 2016; Sachweh, 2016). En el caso de las pensiones, esta disputa puede organizarse en torno a la tensión entre la *justicia de mercado*, que legitima la asignación de beneficios según el esfuerzo, la contribución y la responsabilidad individual, y la *justicia política*, que enfatiza la igualdad, la necesidad y la intervención colectiva frente a los riesgos sociales (Lane, 1986). Esta investigación analiza la estructuración discursiva del debate legislativo chileno sobre la reforma previsional de 2022-2025, entendido como una arena en la que distintos actores movilizan concepciones de justicia social, criterios de merecimiento y estrategias de legitimación para defender, reformar o disputar la capitalización individual.

Chile constituye un caso especialmente relevante para analizar esta disputa normativa. Desde la reforma de 1981, el sistema previsional chileno se ha organizado en torno a cuentas individuales administradas por actores privados, convirtiéndose en una experiencia extrema de privatización y comodificación del bienestar (Arenas, 2010; Borzutzky, 2019; Mesa-Lago & Bertranou, 2016). Sus bases ideológicas se anclaron en una crítica neoliberal al colectivismo y en la promesa de libertad individual, eficiencia privada y correspondencia entre el esfuerzo personal y la recompensa futura (Borzutzky, 2005). Históricamente, este diseño ha sido cuestionado por sus bajas pensiones, desigualdades de género y de clase, persistiendo institucionalmente pese a la alta conflictividad social y a sucesivos intentos de reforma (Borzutzky, 2019; Larrañaga, 2024; Rozas & Maillet, 2019). En los últimos años, el estallido social de 2019, los retiros de fondos previsionales durante la pandemia y la discusión constitucional reactivaron el conflicto sobre la propiedad individual, la solidaridad, el mérito y el rol del Estado, desplazando el debate previsional hacia una disputa explícita por los fundamentos morales del sistema (Barozet, 2025; Kay & Borzutzky, 2022; Rozas-Bugueño & Maillet, 2024). La reforma impulsada por el gobierno de Gabriel Boric en 2022 prometió una transformación estructural mediante la creación de un sistema mixto y de nuevos componentes de solidaridad, pero la Ley N° 21.735, aprobada en 2025, mantuvo la capitalización individual como núcleo del diseño previsional y al sector privado como principal administrador de los fondos (Vela, 2025).

Hasta ahora, las investigaciones sobre pensiones en Chile se han enfocado en el diseño institucional y la trayectoria política del sistema (Borzutzky, 2005, 2019; Mesa-Lago & Bertranou, 2016), sus resultados financieros y tasas de reemplazo (Benavides & Valdés, 2018; Larrañaga, 2024), las brechas socioeconómicas y de género (Parada-Contzen, 2023), las movilizaciones sociales contra las AFP (López-González & Vélez-Maya, 2025; Rozas & Maillet, 2019), las preferencias ciudadanas sobre diseños previsionales y administración de fondos (Domínguez, 2017; Parada-Contzen & Sanhueza, 2025), las actitudes frente a la justicia de mercado y el mérito previsional (Castillo et al., 2019, 2025, 2026), y los discursos mediáticos o expertos en torno a la reforma (Campos-Rojas & González-Arias, 2022; González Arias & Campos Rojas, 2020). Esta literatura ha mostrado que la crítica a las bajas pensiones convive con una adhesión persistente a criterios meritocráticos y contributivos, especialmente en torno a la propiedad de los fondos y al vínculo entre la cotización individual y el beneficio futuro (Castillo et al., 2019; Kay & Borzutzky, 2022). Sin embargo, se sabe menos sobre cómo estos principios de justicia se articulan en el debate legislativo, cómo se forman coaliciones discursivas en torno a ellos y qué estrategias emplean los actores para legitimar la persistencia o la transformación del modelo. El presente estudio aborda esa brecha analizando el debate parlamentario de la última reforma previsional chilena como un espacio privilegiado para observar la producción de hegemonía discursiva.

El argumento central de esta investigación sostiene que la resiliencia de la capitalización individual depende, en parte, de su capacidad para ordenar discursivamente los límites de la reforma. En el debate legislativo, las coaliciones defienden intereses y diseños técnicos, mientras articulan líneas argumentales relativamente estables sobre lo que consideran justo, viable y moralmente aceptable (Béland, 2005; Hajer, 1997; Schmidt, 2008). Estos argumentos combinan concepciones amplias de superioridad moral, criterios concretos de merecimiento (como la reciprocidad o la necesidad) y estrategias de legitimación como la racionalización o la narrativización (Boltanski et al., 2006; Vaara et al., 2006; Van Leeuwen, 2007; van Oorschot, 2000). Desde esta perspectiva, la convergencia pragmática del debate constituye un foco central: la solidaridad puede ingresar al repertorio de la reforma bajo condiciones discursivas que preservan la primacía de la propiedad individual, la capitalización y la sostenibilidad financiera.

Por lo tanto, la pregunta de investigación se plantea de la siguiente manera: ¿qué concepciones de justicia social y qué estrategias de legitimación utilizan las coaliciones discursivas en el debate legislativo en torno a la última reforma de pensiones chilena (2022-2025), y qué revela esta articulación sobre la robustez ideacional de la capitalización individual? Para responderla, el estudio articula cuatro hipótesis. En primer lugar, se postula que el debate se estructura en tres coaliciones (promercado, centroizquierda e izquierda estructural) ancladas en visiones normativas divergentes sobre la justicia social (H1). Para lograr legitimidad, estas coaliciones despliegan repertorios estratégicos diferenciados (H2) y los aterrizan en lógicas concretas de asignación mediante distintos criterios de condicionalidad CARIN (H3). Finalmente, se argumenta que el debate experimentará un proceso de convergencia pragmática con el tiempo, en el que las lógicas de solidaridad quedarán subordinadas a la preeminencia de la justicia de mercado, evidenciando la robustez ideacional del modelo (H4).

Para evaluar estas hipótesis, la presente investigación utiliza una metodología de análisis de redes discursivas (Leifeld, 2017, 2020), combinando codificación cualitativa asistida por LLM, validación manual y modelos multinivel de clasificación cruzada (Hayes, 2025; Tranmer et al., 2014). Esta estrategia permite analizar grandes volúmenes de deliberación legislativa sin abandonar la interpretación sociológica de los discursos, observando simultáneamente la estructura relacional de las coaliciones, los conceptos que organizan el debate y los cambios temporales en los repertorios de justificación. El estudio realiza cuatro contribuciones principales. En primer lugar, profundiza en la comprensión de cómo las concepciones de justicia social actúan como motores de legitimación en el discurso político. En segundo lugar, permite analizar las dinámicas de dichos discursos como redes relacionales en el parlamento. En tercer lugar, aporta evidencia empírica situada al estudio de las pensiones en Chile, ofreciendo una lectura del proceso legislativo sobre la reforma previsional más ambiciosa de las últimas décadas. Por último, propone una estrategia metodológica cualitativa-computacional para procesar la deliberación política a gran escala mediante inteligencia aumentada.

El presente manuscrito se organiza de la siguiente manera. La segunda sección profundiza en los antecedentes conceptuales y empíricos de la investigación. La tercera sección detalla la estrategia metodológica. La cuarta sección presenta los resultados del modelamiento topológico y temporal de las redes. Finalmente, la quinta sección discute los hallazgos en relación con la literatura pertinente y presenta las conclusiones y limitaciones del estudio.

## **1\. La dimensión moral y normativa en el debate previsional** {#1.-la-dimensión-moral-y-normativa-en-el-debate-previsional}

### **1.1. Justicia de mercado vs. Justicia política: Los mercados como economías morales** {#1.1.-justicia-de-mercado-vs.-justicia-política:-los-mercados-como-economías-morales}

Los arreglos del Estado de bienestar operan como la cristalización institucional de un orden moral (Sachweh, 2016). Sus políticas sociales poseen una orientación normativa inherente que resuena con los valores de la ciudadanía (Schmidt, 2008). Estas concepciones compartidas son objeto de constantes disputas discursivas en las esferas públicas. El debate político se convierte así en una arena en la que los actores movilizan estratégicamente distintas nociones del valor moral para legitimar o disputar el diseño institucional vigente (Béland, 2005; Liebig & Sauer, 2016).

Esta contienda discursiva puede entenderse a partir de la tensión entre dos paradigmas contrapuestos: la justicia de mercado y la justicia política (Lane, 1986). La justicia de mercado opera bajo una lógica procedimental pura, concibiendo la distribución ideal como el resultado natural de transacciones competitivas. Su fundamento normativo es el principio de los méritos ganados, donde el sistema recompensa la productividad y el esfuerzo individual. En el caso previsional, esta lógica convierte la capitalización individual en un mecanismo normativo de valorización de los sujetos, donde el saldo acumulado puede presentarse como indicador legítimo de esfuerzo, responsabilidad y mérito (Fourcade & Healy, 2007). En contraposición, la justicia política obliga a considerar a la sociedad en su conjunto. Este paradigma se rige por los criterios de igualdad y necesidad, exigiendo la intervención estatal mediante mecanismos redistributivos para corregir las fallas del mercado y proteger a quienes carecen de recursos (Lane, 1986).

Para analizar esta disputa en el debate legislativo, se identificarán los distintos órdenes de justificación que emplean los actores (Boltanski et al., 2006). Por un lado, los discursos de la *justicia de mercado* pueden presentarse a través del *Mundo Mercantil*, que plantea como valores supremos la competencia, la riqueza y la libertad de transacción, y del *Mundo Industrial*, que evalúa la grandeza a través de la eficiencia técnica y el rendimiento futuro. Por otro lado, la *justicia política* puede materializarse a través del *Mundo Cívico*, cuyo valor supremo es lo colectivo, la solidaridad y los derechos ciudadanos (Boltanski et al., 2006).

La evidencia empírica en política social respalda la utilidad de analizar las pensiones como instituciones moralmente cargadas. Históricamente, la jubilación ha desempeñado un papel central en la economía moral de la sociedad salarial, al prometer reciprocidad futura a quienes trabajan formalmente (Kohli, 1987). A nivel comparado, las evaluaciones ciudadanas del bienestar se organizan en torno a repertorios morales diversos, como la reciprocidad, la igualdad y la responsabilidad individual (Taylor-Gooby et al., 2019). En el campo previsional, las reformas han sido moldeadas por narrativas institucionales sobre igualdad obrera, planificación estatal, sostenibilidad y equidad, mostrando que el lenguaje técnico de las pensiones suele transportar concepciones sobre merecimiento, solidaridad y justicia colectiva (Anderson, 2018; Ring et al., 2020). Incluso frente a desafíos demográficos y financieros similares, los informes de expertos pueden justificar cursos de acción divergentes mediante lógicas mercantiles, industriales, cívicas o domésticas, privilegiando distintos equilibrios entre eficiencia, correspondencia contributiva, solidaridad y redistribución (Väänänen & Liukko, 2022). En Chile, la resignificación de la solidaridad en las políticas sociales de la Concertación muestra que un valor históricamente asociado a la justicia social puede traducirse discursivamente en esquemas focalizados compatibles con la responsabilidad individual (Román Brugnoli & Osorio Gonnet, 2015). De esta forma, los órdenes de justificación permiten observar empíricamente cómo los actores traducen los conflictos distributivos en principios morales superiores.

### **1.2. La condicionalidad de la seguridad social en la vejez** {#1.2.-la-condicionalidad-de-la-seguridad-social-en-la-vejez}

La disputa entre la *justicia de mercado* y la *justicia política* requiere una operacionalización orientada a lógicas concretas de asignación de recursos. En el debate legislativo, los parlamentarios pueden articular sus concepciones de justicia mediante la condicionalidad, definiendo de manera selectiva "quién merece qué". Mientras que los órdenes de justificación permiten identificar los principios superiores que legitiman una política, los criterios CARIN (van Oorschot, 2000\) permiten observar cómo esos principios se traducen en evaluaciones sobre sujetos, trayectorias y necesidades específicas. Se utilizará la adaptación realizada por Knotz et al. (2022), que propone seis criterios fundamentales mediante los cuales se legitima la asignación de apoyo estatal: *Control* (situación de dificultad causada por la acción o inacción de la persona), *Actitud* (docilidad o agradecimiento ante el apoyo como gestos simbólicos), *Reciprocidad* (grado de contribución previa a los demás), *Esfuerzo* (acciones actuales que contribuyen a los demás), *Identidad* (grado de pertenencia a grupos sociales) y *Necesidad* (nivel de dificultad de la persona).

La literatura actitudinal ha abordado ampliamente la relación entre los criterios de merecimiento y las políticas de pensiones en el contexto europeo. Tradicionalmente, los adultos mayores son categorizados como un grupo altamente merecedor, ya que no controlan su situación de necesidad (el envejecimiento biológico) y se asume que ya han contribuido a la sociedad a lo largo de su vida (Meuleman et al., 2020; van Oorschot, 2006). Dado esto, existe un amplio consenso en torno a que el sustento de las necesidades de la vejez es responsabilidad del gobierno (Deeming, 2018; Ebbinghaus & Naumann, 2020; van Oorschot et al., 2022). Sin embargo, en regímenes conservadores, la asignación de recursos suele vincularse al criterio de reciprocidad, atando el monto de los beneficios a las contribuciones previas (Van Hootegem et al., 2024). El eje ideológico opera como estructurador de estos criterios: mientras la derecha política exige mayor condicionalidad y otorga primacía al mérito (Reeskens & van Oorschot, 2013), la izquierda tiende a abogar por un financiamiento solidario, priorizando la cobertura de la necesidad material (Wiß et al., 2025).

La evidencia empírica muestra que estos criterios también operan como repertorios discursivos para construir beneficiarios legítimos e ilegítimos. La aceptación de prestaciones sociales combina principios de necesidad con exigencias de responsabilidad personal, esfuerzo y ausencia de abuso (Sachweh et al., 2006). En el campo previsional, estas lógicas se traducen en narrativas sobre el "jubilado merecedor" o el "trabajador esforzado", capaces de simplificar debates técnicos y de acoplar problemas, soluciones y grupos objetivo (Blum, 2019; Hagelund & Grødem, 2019). Asimismo, las políticas de austeridad pueden repolitizarse mediante relatos morales que distinguen entre sujetos "merecedores" y "no merecedores", lo que muestra que la condicionalidad opera también como una disputa discursiva sobre la legitimidad del apoyo estatal (Gaffney, 2025; Kuhlmann & Blum, 2022; Wiggan, 2012).

En Chile, un país caracterizado por una alta privatización del bienestar (Ferre, 2023), la evidencia empírica muestra la profunda penetración de lógicas condicionales en la sociedad. Si bien existe una demanda ciudadana de una mayor intervención estatal para aumentar las pensiones, persiste simultáneamente una fuerte justificación del mecanismo del mérito, que legitima que quienes aportaron más al sistema reciban una mejor jubilación (Castillo et al., 2019). Este hallazgo es especialmente relevante porque muestra que la crítica a las pensiones bajas puede coexistir con criterios distributivos altamente individualizados vinculados al merecimiento. Aunque la justificación de esta desigualdad previsional experimentó fluctuaciones tras el estallido social de 2019, la adhesión a la lógica meritocrática ha retomado una trayectoria ascendente en los años recientes (Castillo et al., 2025, 2026).

Históricamente, la aplicación del marco CARIN se ha restringido a la medición de actitudes ciudadanas mediante encuestas o experimentos de viñetas, con una fuerte concentración en el contexto europeo. Recientemente, se ha destacado la urgencia de ampliar este marco a metodologías cualitativas para evitar reduccionismos (Laenen et al., 2019), lo que ha impulsado estudios centrados en entrevistas, focus groups o debates en línea (Michoń, 2021; Siviş, 2022; Summers et al., 2025; Theiss, 2023). En particular, Hilmar (2025) utiliza métodos computacionales para identificar criterios de merecimiento a partir de datos masivos, lo que respalda un enfoque como el de este estudio. Metodológicamente, la presente investigación operacionaliza este marco siguiendo la propuesta de Laenen et al. (2019), identificando los criterios de merecimiento en declaraciones en las que el hablante emite una afirmación sobre una política social y plantea una justificación de si el beneficio debe otorgarse. De esta forma, CARIN permite analizar cómo las coaliciones legislativas emplean criterios concretos de contribución, responsabilidad, necesidad y pertenencia.

## 

## 

## 

## 

## 

## 

## 

## 

## **2\. Resiliencia institucional y legitimación discursiva: el rol de las ideas** {#2.-resiliencia-institucional-y-legitimación-discursiva:-el-rol-de-las-ideas}

### **2.1. Robustez neoliberal y el rol de las ideas** {#2.1.-robustez-neoliberal-y-el-rol-de-las-ideas}

Comprender la persistencia de un modelo fuertemente cuestionado, como la capitalización individual chilena, requiere analizar la arquitectura de su inmovilismo. Clásicamente, la literatura ha explicado esta rigidez mediante el concepto de *path dependence*, sosteniendo que los costos hundidos, el arraigo burocrático y las rutinas institucionales bloquean las transformaciones estructurales (Peters et al., 2005). No obstante, este enfoque tiende a asumir una inercia estática que oculta las pugnas y los conflictos activos. Frente a ello, en esta investigación se comprende la supervivencia de un régimen en crisis bajo la noción de *robustez ideacional* (Migone et al., 2024): una resiliencia dinámica en la que el modelo incorpora cambios paramétricos y reformas de primer orden para resguardar su núcleo normativo frente a crisis de legitimidad. 

En el escenario chileno, la robustez ideacional puede entenderse como un cerrojo sistémico sostenido por tres pilares interdependientes (Madariaga, 2020): los intereses materiales del empresariado y la industria previsional, los candados de las instituciones políticas y las ideas económicas dominantes. Cuando uno de estos componentes es amenazado, los pilares restantes se activan para absorber el impacto y forzar la acomodación del régimen. En el caso previsional, la industria de las AFP acumuló poder estructural e instrumental durante décadas mediante su peso financiero, puertas giratorias y su capacidad de incidencia ante instancias asesoras (Bril-Mascarenhas & Maillet, 2019). Desde el lado ciudadano, la trayectoria privatizada del sistema parece haber moldeado expectativas normativas compatibles con el mérito contributivo, reforzando la persistencia ideacional del modelo (Castillo et al., 2019).

Las ideas, por tanto, operan como el mecanismo que convierte las restricciones impuestas por los intereses materiales y las instituciones en políticamente defendibles, técnicamente razonables y moralmente aceptables. La literatura ideacional ha mostrado que las ideas influyen en la política social al construir intereses, ofrecer mapas de ruta y legitimar alternativas ante públicos específicos (Béland & Mandelkern, 2024). La resiliencia neoliberal depende de esta capacidad de adaptación discursiva: sus planteamientos sobreviven a las crisis al convertirse en ideas de fondo que delimitan qué alternativas parecen viables, responsables o realistas (Schmidt, 2016). En el contexto previsional chileno, Castiglioni (2018) argumenta que la predominancia de la ideología de mercado entre los tomadores de decisiones ha contribuido a la persistencia de la capitalización individual. Esta persistencia ideacional es crucial para comprender cómo el modelo puede absorber reformas sin abandonar su principio distributivo.

Si bien los intereses y las instituciones imponen límites fácticos al cambio, es el pilar de las ideas el que otorga viabilidad política a dichas restricciones. Son estas las que legitiman el ordenamiento institucional restrictivo, traduciendo los intereses de la industria en preferencias políticas aparentemente objetivas e incuestionables ante la sociedad (Madariaga, 2020). La supervivencia de un régimen de bienestar depende, por tanto, de la capacidad de los actores para dominar la arena discursiva (Béland, 2005). El presente análisis se centrará empíricamente en esa arena, con el objetivo de mapear las concepciones de justicia social que predominan en el debate legislativo chileno.

### **2.2 El discurso como poder y hegemonía** {#2.2-el-discurso-como-poder-y-hegemonía}

Para comprender la dinámica de las instituciones, es fundamental analizar los procesos ideacionales que las sostienen. Desde el institucionalismo discursivo, la estabilidad o la transformación de una política descansa en la interacción constante entre ideas cognitivas y normativas (Schmidt, 2008). Mientras las primeras ofrecen mapas de ruta técnicos sobre "qué hacer" para resolver problemas específicos, las ideas normativas operan en el plano valórico, definiendo lo que es bueno y legitimando las soluciones técnicas ante la sociedad. El éxito de un programa político requiere un discurso comunicativo que demuestre que resuena con los ideales y valores del sistema político, junto con un discurso coordinativo capaz de articular acuerdos entre élites y actores organizados (Schmidt, 2002, 2008).

Este proceso de legitimación es impulsado por emprendedores de políticas, actores que operan estratégicamente para romper o defender la inercia del *statu quo*. Estos sujetos ejecutan una labor deliberada de *framing*, conectando soluciones técnicas con repertorios ideológicos y símbolos culturales preexistentes (Béland, 2005). El *framing* es dialógico y preventivo: se construye anticipando y neutralizando las críticas de los oponentes, logrando que alternativas que podrían resultar impopulares se perciban como culturalmente aceptables y socialmente necesarias (Béland, 2005). Algunas ideas adquieren una mayor capacidad articuladora al funcionar como imanes de coalición, debido a su polisemia y alta valencia moral, lo que permite reunir a actores con intereses heterogéneos bajo un vocabulario compartido (Béland & Cox, 2016). Cuando estas estrategias son adoptadas de forma relativamente estable por diversos actores, se conforman *coaliciones discursivas* unidas por líneas argumentales comunes (Hajer, 1997).

En esta contienda, el poder político opera, en parte, mediante el lenguaje. Carstensen y Schmidt (2016) plantean que este ejercicio adquiere distintas dimensiones. El *poder a través de las ideas* funciona mediante la persuasión y el convencimiento; el *poder sobre las ideas* se refiere a la capacidad de ciertos actores para controlar el significado de las ideas, forzando su aceptación o excluyendo visiones alternativas; y el *poder en las ideas* alude a la autoridad que poseen ciertas ideas para estructurar lo que las élites y la ciudadanía consideran lógico y moralmente correcto. Esta última dimensión es especialmente relevante para analizar la hegemonía, pues permite comprender cómo ciertos discursos dejan de aparecer como posiciones políticas situadas y pasan a operar como sentido común.

La evidencia empírica muestra que el poder ideacional puede observarse en el ámbito de la política social. En el área de las pensiones, los cambios de hegemonía discursiva han sido rastreados mediante redes de actores y creencias, mostrando cómo viejos consensos pueden ser desplazados por procesos de polarización, migración de actores clave y formación de nuevas coaliciones (Leifeld, 2013). A su vez, las narrativas de crisis demográfica pueden instalar la necesidad de reformar, aunque su éxito depende de cómo las reglas institucionales filtran las alternativas disponibles (Béland, 2019). En América Latina, la estructuración de proyectos hegemónicos de austeridad previsional y la apertura de alternativas solidarias muestran que el espacio de políticas se transforma cuando coaliciones promercado, expertos, movimientos sociales y eventos críticos disputan el monopolio de los marcos dominantes (Costa & Wiggan, 2024; Rozas-Bugueño & Maillet, 2024). Estos procesos también involucran la disputa por conceptos polisémicos, como la sostenibilidad financiera y la solidaridad, que pueden actuar como imanes de coalición al adquirir sentidos rivales a través de narrativas de declive, control o justicia social (Béland & Cox, 2016; Lee & Kim, 2026). Por tanto, el discurso debe entenderse como una arena en la que se forman coaliciones, se estabilizan conceptos y se jerarquizan significados políticamente eficaces.

Según Hajer (1997), un discurso alcanza hegemonía institucional cuando logra dos hitos consecutivos: la *estructuración*, que ocurre cuando impone sus categorías y su vocabulario como marco legítimo del debate; y la *institucionalización*, cuando esas ideas se materializan en leyes, reglamentos o prácticas organizacionales. Esta investigación se enfocará en la *estructuración* discursiva de las coaliciones legislativas; es decir, en su capacidad para situar sus concepciones de justicia social en el centro del debate previsional, desplazar los marcos rivales y definir los límites de lo políticamente aceptable.

### **2.3 Estrategias de legitimación y los discursos tecnocráticos** {#2.3-estrategias-de-legitimación-y-los-discursos-tecnocráticos}

La consolidación del poder ideacional requiere mecanismos argumentativos capaces de persuadir, coordinar las élites y neutralizar la disidencia. Las estrategias de legitimación permiten observar cómo los criterios de justicia se presentan como razonables, necesarios o moralmente aceptables. La legitimación institucional puede desplegarse mediante cinco estrategias discursivas: la *racionalización*, que justifica las decisiones apelando a su utilidad técnica, eficiencia y resultados proyectados; la *moralización*, que evalúa las políticas basándose en sistemas de valores y principios éticos; la *narrativización*, que dota a las medidas abstractas de una estructura dramática o histórica para hacerlas comprensibles; la *autorización*, que recurre al respaldo de expertos, leyes o entidades abstractas; y la *normalización*, que presenta cambios radicales como comportamientos naturales o ineludibles (Vaara et al., 2006; Van Leeuwen, 2007).

Estas estrategias son especialmente relevantes cuando se articulan con formas tecnocráticas de legitimación. En debates previsionales, el conocimiento experto puede presentar conflictos distributivos como problemas de eficiencia, sostenibilidad o factibilidad técnica, desplazando las preguntas sobre justicia, beneficiarios y responsabilidad política (Tortola, 2020). En este sentido, la racionalización y la autorización pueden actuar como recursos para estabilizar alternativas institucionales y proteger su base normativa de la deliberación pública (Lemke, 2012; Vaara et al., 2006).

La evidencia empírica muestra que la legitimación de las reformas previsionales recurre con frecuencia a la racionalización, la autorización y la moralización. Los gobiernos han justificado reformas regresivas con argumentos de sostenibilidad financiera y equidad generacional, apoyándose en comisiones expertas y metáforas nacionales para hacer comunicable la austeridad (Ring et al., 2020). En esa misma línea, las recomendaciones expertas y supranacionales tienden a privilegiar ideas cognitivas de sostenibilidad fiscal por encima de argumentos normativos de equidad, transformando la contención del gasto en un imperativo técnico difícil de disputar (Mulligan et al., 2026; Väänänen & Liukko, 2022). En Chile, las comisiones asesoras presidenciales sobre pensiones han estado dominadas por economistas de élite y han tendido a canalizar la presión reformista hacia ajustes paramétricos (Garber, 2021). Asimismo, los expertos económicos han intervenido en la esfera pública mediante estrategias orientadas a deslegitimar reformas estructurales y defender el sistema privado (Campos-Rojas & González-Arias, 2022). Estos antecedentes sugieren que la experticia puede operar como una forma de *autorización* y *racionalización*, aunque su eficacia depende de cómo logra articularse con argumentos morales sobre responsabilidad, mérito o justicia (Costa & Wiggan, 2024; Gaffney, 2025).

En esta investigación, además de analizar cómo las ideas estructuran el debate y delimitan las coaliciones discursivas, se examinarán las estrategias de legitimación empleadas para hacer que dichas ideas resulten persuasivas. Esto permitirá identificar si existe una asociación entre las concepciones de justicia social y repertorios discursivos específicos, como la *moralización* o la *racionalización*.

En conjunto, los marcos presentados cumplen funciones analíticas diferenciadas en el diseño de la investigación. El institucionalismo discursivo y el enfoque de coaliciones permiten comprender la estructuración del debate; la distinción entre *justicia de mercado* y *justicia política* delimita la oposición normativa central; los órdenes de justificación y los criterios CARIN permiten operacionalizar empíricamente esas concepciones de justicia; y las estrategias de legitimación permiten analizar cómo se justifican dichas ideas.

## **3\. El debate previsional chileno: la conformación de tres coaliciones** {#3.-el-debate-previsional-chileno:-la-conformación-de-tres-coaliciones}

La tensión entre la justicia de mercado y la justicia política encuentra en la trayectoria del sistema previsional chileno una manifestación empírica crítica. La configuración y defensa de la capitalización individual en Chile ha operado como un campo de batalla discursivo, estructurado en torno a distintas coaliciones que movilizan repertorios morales para definir los contornos de la seguridad social. La reconstrucción histórica que sigue permite derivar expectativas analíticas sobre esas coaliciones, cuya existencia, composición y fronteras serán evaluadas empíricamente en el estudio. Desde la imposición del modelo en dictadura, sus reformas (2008 y 2025\) y los intentos fallidos de transformación estructural (2015 y 2018), la disputa previsional ha evidenciado la competencia constante entre visiones antagónicas de justicia distributiva (Borzutzky, 2019; Larrañaga, 2024; Mesa-Lago & Bertranou, 2016).

Durante las primeras décadas de la posdictadura, la administración y legitimación del modelo fueron conducidas por la Concertación de Partidos por la Democracia. Los tecnócratas de este sector amortiguaron demandas sociales complejas y polarizadas, al traducirlas a un lenguaje técnico que despolitizó la gestión pública y estabilizó el régimen (Silva, 2006). Este sector desplegó un marco interpretativo que redefinió el concepto histórico de solidaridad, vaciándolo de su componente redistributivo estructural para transformarlo en un mecanismo de responsabilización individual (Román Brugnoli & Osorio Gonnet, 2015). Asimismo, los hacedores de políticas de la centroizquierda internalizaron y respaldaron los pilares del modelo de protección social heredado de la dictadura, tales como la privatización y la focalización (Castiglioni, 2018). Si bien movilizaron ideas de protección social frente al riesgo, mantuvieron un fuerte ideal del mérito cristalizado en la preservación de los fondos individuales. Así, las comisiones asesoras y la creación de políticas como el Pilar Solidario en 2008 canalizaron la presión reformista hacia ajustes paramétricos, justificando la asistencia focalizada ante la necesidad material extrema y protegiendo el núcleo de la capitalización privada (Garber, 2021; Martin & Alfaro, 2017).

El quiebre de esta hegemonía discursiva se materializó con la intensificación del conflicto social en torno al movimiento NO+AFP a partir de 2016\. Este movimiento impugnó la legitimidad del modelo, desplazando el eje de justificación hacia el principio de necesidad material y reclamando por las pensiones bajas otorgadas por el sistema (Matus, 2020). Estratégicamente, el movimiento apeló a la memoria para desmantelar la supuesta libertad de elección del mercado, reconceptualizando la capitalización individual como un sistema de ahorro forzoso impuesto en dictadura y basado en la especulación financiera (López-González & Vélez-Maya, 2025). Su innovación táctica consistió en disputar la arena de las élites, presentando una propuesta técnica de reparto basada en la solidaridad intergeneracional tripartita (Rozas & Maillet, 2019).

Frente a la amenaza estructural, la industria de las AFP y las élites políticas conservadoras reaccionaron desplegando una defensa ideacional robusta. Por un lado, promovieron la despolitización del conflicto, adoptando una postura corporativa de servicio al cliente y apelando a la educación previsional y la rentabilidad (Matus, 2020). Por otro lado, movilizaron el miedo y la indignación moral: expertos económicos atacaron las propuestas solidarias acusándolas de ser infactibles debido al envejecimiento demográfico y de representar un riesgo de quiebra financiera estatal que asumirían las próximas generaciones (Campos-Rojas & González-Arias, 2022; Rozas & Maillet, 2019). Simultáneamente, blindaron la capitalización exaltando el mérito y advirtiendo que toda reforma distributiva constituía una expropiación de la propiedad privada de los cotizantes (Campos-Rojas & González-Arias, 2022). Esta narrativa hegemónica ha contado con el respaldo de una cobertura mediática fuertemente sesgada a su favor (González Arias & Campos Rojas, 2020\) y de un vasto poder de influencia institucional, dado que las AFP administran cerca del 70% del PIB de Chile (Bril-Mascarenhas & Maillet, 2019; Kay & Borzutzky, 2022).

El estallido social de 2019 quebró transitoriamente estas correlaciones de poder. El repertorio de las políticas públicas se expandió, impulsando al bloque promercado a aceptar lógicas de solidaridad y un sistema mixto para mantener la paz social (Rozas-Bugueño & Maillet, 2024). Sin embargo, durante la pandemia, los sucesivos retiros de fondos (que sustrajeron aproximadamente el 18% del PIB nacional de las AFP \[Larrañaga, 2024\]) exacerbaron el sentido de propiedad individual sobre los ahorros (Barozet, 2025; Kay & Borzutzky, 2022). Esto derivó en el surgimiento de iniciativas ciudadanas como "Con mi plata no", que reactivó la dicotomía moral entre "los que trabajan" y "los que lo quieren todo gratis" (Barozet, 2025; Godoy, 2023). La última reforma de pensiones (Ley 21.735), con ambiciosas intenciones de reforma estructural, no logró alterar la base del sistema de capitalización individual. Pese a las intenciones solidarias, la mayor proporción de las nuevas cotizaciones obligatorias sigue bajo el control de las AFP y es rentabilizada (Vela, 2025).

En términos históricos, el panorama discursivo chileno sugiere la presencia de tres grandes polos de articulación: (1) una *izquierda reformista estructural* fundamentada en el universalismo y la solidaridad intergeneracional; (2) una *centroizquierda* anclada en la tecnocracia, la selectividad y una solidaridad supeditada a la necesidad material extrema; y (3) un *bloque promercado* defensor acérrimo del mérito, la propiedad privada y la acumulación de mercado.

A partir de la revisión de antecedentes y en función de la pregunta de investigación planteada, se postulan las siguientes hipótesis relativas a la estructuración del debate durante la reforma de pensiones:

* *H1*: Se espera que el debate se estructure en torno a tres coaliciones discursivas alineadas con facciones históricas: el bloque promercado se alineará fuertemente con la *justicia de mercado*, la izquierda estructural con la *justicia política*, y la centroizquierda articulará una postura mediadora que hibrida elementos de ambas concepciones.

* *H2*: Las coaliciones discursivas identificadas desplegarán repertorios híbridos pero diferenciados de estrategias de legitimación. Se espera que la combinación relativa de *racionalización*, *moralización*, *narrativización*, *autorización* y *normalización* varíe sistemáticamente entre coaliciones, expresando distintas formas de justificar sus posiciones en el debate previsional.

* *H3:* Los criterios de merecimiento (CARIN) permitirán observar cómo las visiones macroestructurales de justicia se traducen en evaluaciones concretas de contribución, responsabilidad y necesidad. Se espera que los argumentos asociados a la *justicia de mercado* enfaticen *reciprocidad*, *esfuerzo* y *control*, mientras que los argumentos asociados a la *justicia política* enfaticen *necesidad*.

* *H4*: A medida que avanza la tramitación legislativa, los argumentos fundamentados en la *justicia de mercado* (mérito, propiedad privada y capitalización) mantienen su preeminencia, subordinando discursivamente las lógicas de solidaridad y orientando una convergencia pragmática del resto de los actores.

## **4\. Metodología** {#4.-metodología}

### **4.1 Datos** {#4.1-datos}

| Tabla 1 *Resumen de datos* |  |  |  |
| ----- | :---: | :---: | :---: |
| Institución | Discusión en Sala | Comisión Trabajo y Previsión Social | Comisión Hacienda |
| Cámara de Diputados | 3 | 32 | 6 |
| Senado | 1 | 41 | 9 |

Para esta investigación, se utilizarán todos los datos discursivamente relevantes de la tramitación de la Ley N° 21.735. Para evaluar la relevancia de los datos, se revisó cada documento de la tramitación, incluidas actas de sesión, informes externos adjuntos y oficios. El dataset central para el análisis se compondrá de las transcripciones de cada sesión (abiertas y técnicas). En total, en la Cámara de Diputados se discutió el proyecto en tres ocasiones; en el Senado, en una; y cuatro comisiones técnicas analizaron el proyecto de ley, cada una con múltiples sesiones documentadas en video. Cada una de estas sesiones suele durar entre una y tres horas, con largas intervenciones (\~3-5 minutos por parlamentario) y, en el caso de las comisiones técnicas, con presentaciones de expertos o de integrantes de la sociedad civil.

Para procesar y limpiar la información ya transcribida, se desarrolló una librería de Python, generalizable a otros proyectos de ley, [disponible en este enlace](https://github.com/ismaelaguayob/bcn-scraper). Esta herramienta permite la extracción automatizada y el preprocesamiento de la información legislativa, recuperando datos de los parlamentarios y de las sesiones, obteniendo como resultado una base de datos estructurada por intervención y libre de artefactos de transcripción. En el caso de las sesiones técnicas, que solo están en formato de video, se diseñó una pipeline de *speech-to-text* y *automatic speaker recognition* (ASR) que, a partir de los videos descargados de SenadoTV o Canal CDTV, obtiene automáticamente un formato análogo al obtenido con la librería. Dado que la identificación de hablantes es una fuente potencial de error, esta etapa se revisará manualmente, priorizando la verificación de nombres, organizaciones y cortes de intervención. Los videos que no alcancen una calidad de detección de hablantes satisfactoria serán excluidos del análisis principal.

### **4.2 Variables** {#4.2-variables}

Esta investigación está fuertemente inspirada en la metodología de análisis de redes discursivas (DNA por sus siglas en inglés), una combinación entre análisis cualitativo temático y modelamiento de redes. Siguiendo a Leifeld (2017), la unidad principal de análisis son las declaraciones: exposiciones verbales o escritas de descontento o apoyo a una política. Las intervenciones que componen nuestro dataset pueden incluir más de una declaración cuando abarcan múltiples conceptos o justificaciones diferenciables. A continuación, se describen las variables que componen una declaración en el DNA, sumado a cómo se van a operacionalizar en nuestra investigación:

1. Actores: las personas u organizaciones que emiten la declaración. En este caso, corresponden a parlamentarios e invitados a instancias legislativas, considerando, según corresponda, su partido, institución u organización.

2. Conceptos: representación abstracta de los conceptos en discusión. Se elaborará de forma deductiva un libro de códigos de conceptos, a partir de las categorías CARIN, los mundos comunes (Boltanski et al., 2006\) y la evidencia discursiva nacional. Este se enriquecerá de forma iterativa a medida que se codifiquen las intervenciones.

3. Acuerdo: variable dicotómica que mide el sentimiento del actor. Es positivo (1) si se refiere al concepto de forma afirmativa, mientras que es negativo (0) si le atribuye una connotación negativa o lo rechaza. 

4. Tiempo o fecha: cada intervención cuenta con un marcador temporal dentro de la sesión, y cada sesión tiene una fecha determinada. Para el análisis, el tiempo se tratará de forma discreta mediante intervenciones, sesiones, etapas legislativas e hitos del proceso.

Adicionalmente, se codificarán las estrategias discursivas empleadas por los actores analizados (Vaara et al., 2006; Van Leeuwen, 2007), como atributo de la arista entre un actor y un concepto. Como se abordó en la sección 2.3, se identificarán estrategias de *moralización*, *racionalización*, *narrativización*, *normalización* y *autorización*.

### **4.3 Estrategia de análisis** {#4.3-estrategia-de-análisis}

#### *4.3.1 Estrategia de codificación y validación* {#4.3.1-estrategia-de-codificación-y-validación}

En este estudio se utilizará el DNA para crear una red relacional de actores y conceptos y analizar las coaliciones discursivas presentes en el debate sobre la reforma de pensiones de 2025\. Para construir la red, el primer paso consiste en codificar las declaraciones de los actores analizados y su grado de acuerdo (Leifeld, 2017\) y, en este caso, la estrategia discursiva. Para esto, debido al amplio volumen de datos disponibles, se emplearán LLM para asistir en la codificación inicial, utilizando métricas y validación manual para asegurar la correcta alineación de los resultados del modelo. El modelo se utilizará como apoyo para aplicar un libro de códigos definido teóricamente, con revisión humana y auditoría posterior, manteniendo la interpretación sustantiva bajo responsabilidad del investigador. Este enfoque ya fue utilizado en combinación con DNA, con resultados insatisfactorios para los investigadores (Randerson et al., 2025); no obstante, se siguió un enfoque inductivo para generar los códigos y se recurrió a modelos no razonadores, ambos determinantes de una peor precisión reconocidos en estudios recientes (Hill et al., 2026; Misra et al., 2026; Mustafa et al., 2026; Zhang et al., 2026). Dejar la decisión de las categorías a los modelos puede llevar a una mayor tasa de alucinaciones, a un menor grado de concordancia con los códigos elaborados por humanos y, en especial, dificulta la alineación con los objetivos de investigación, generando categorías sin significancia para la disciplina.

Siguiendo las mejores prácticas de investigación cualitativa realizada con LLM, se asignarán categorías claras y bien definidas mediante prompts estructurados, permitiendo al modelo generar categorías nuevas en casos límite para reducir las alucinaciones[^1] (Ashwin et al., 2025). Sumado a esto, se aislarán los pasos analíticos, como la codificación de declaraciones y de estrategias discursivas, y se solicitarán justificaciones y evidencia textual para cada codificación (Dunivin, 2025). 

Luego, se codificará manualmente una submuestra estratificada de intervenciones, considerando variación por cámara, comisión o sala, etapa legislativa, partido, género y tipo de actor, siguiendo el mismo esquema y libro de códigos (Bosley, 2025). Esta submuestra permitirá construir ejemplos para emplear un enfoque *few-shot[^2]* si es necesario, generar una referencia experta para evaluar el desempeño de los modelos y auditar cualitativamente sus errores. Cuando sea factible, la validación incorporará codificadores humanos adicionales; de no ser posible, se contrastarán las clasificaciones con un segundo o tercer modelo para evaluar consistencia entre sistemas y detectar desacuerdos relevantes. A partir de esto, se estimarán métricas ampliamente utilizadas en tareas de clasificación con LLM (Crupi et al., 2025; Dunivin, 2025; Kristjánsson et al., 2026; Mishra et al., 2025; Woelfle et al., 2024), como precision, recall, F1 score y matrices de confusión respecto de la codificación manual. Además, se calcularán métricas de concordancia entre codificadores humanos y computacionales, como el kappa de Cohen para comparaciones pareadas o medidas de acuerdo para múltiples codificadores, con el objetivo de evaluar la estabilidad del esquema de codificación. Si luego de estos pasos el proceso no resulta convincente, se volverá a la fase de creación del libro de códigos y prompts para alinear al modelo con los objetivos del estudio. Las diferencias entre los códigos del autor, otros codificadores y los modelos se interpretarán como insumos para mejorar el instrumento y como posibles resultados analíticos sobre zonas de ambigüedad discursiva (Soemer et al., 2025).

#### *4.3.2 Análisis descriptivo y modelamiento de patrones discursivos* {#4.3.2-análisis-descriptivo-y-modelamiento-de-patrones-discursivos}

El análisis de los datos codificados se estructurará en fases metodológicas secuenciales y complementarias: una aproximación descriptiva centrada en la topología de la red para caracterizar las coaliciones (H1), un análisis descriptivo de los repertorios de justicia y legitimación, y una batería de modelos estadísticos a nivel de declaración para evaluar asociaciones entre coaliciones, criterios de justicia, estrategias discursivas y etapas legislativas (H2, H3 y H4).

Para evaluar la estructura macro del debate y responder a la primera hipótesis, la red bipartita original (actores-conceptos) se transformará en una proyección unimodal de la congruencia de actores. Dado el sesgo de actividad inherente a la deliberación legislativa, en la que presidentes de comisión o autoridades del Ejecutivo intervienen con mayor frecuencia por obligación institucional, la proyección se normalizará mediante medidas de similitud matemática, tales como el índice de Jaccard o la similitud del coseno. Sobre esta matriz normalizada, se aplicarán algoritmos de detección de comunidades basados en la maximización de la modularidad, como el algoritmo de Louvain (Blondel et al., 2008\) o Leiden (Traag et al., 2019), para delimitar empíricamente las fronteras de las coaliciones discursivas. Este procedimiento permitirá evaluar si la expectativa de tres polos discursivos se expresa en la estructura observada de la red, así como identificar eventuales subdivisiones, desplazamientos o configuraciones alternativas. Una vez particionada la red, se calcularán métricas topológicas clave a nivel de nodo. Particularmente, se utilizará la centralidad de intermediación, o *betweenness centrality* (Freeman, 1977), para poner a prueba la configuración tripartita y el rol de "puente" de la centroizquierda. De manera complementaria, la centralidad de autovector (Bonacich, 1987\) en la proyección de congruencia de conceptos permitirá observar la prominencia estructural inicial de los criterios CARIN en el debate.

Para el modelamiento estadístico, se partirá por estimaciones descriptivas y modelos logísticos simples, avanzando hacia especificaciones más complejas solo cuando los datos lo permitan. Si bien los modelos de grafos aleatorios exponenciales (ERGM) (Lusher et al., 2013\) constituyen una alternativa consolidada para estudiar la formación de lazos en redes, las hipótesis de esta investigación se orientan principalmente a explicar repertorios de justificación en declaraciones concretas. Por ello, se privilegiará un enfoque basado en modelos logísticos multinomiales y, en una segunda etapa, modelos multinivel de clasificación cruzada o *Cross-Classified Mixed-Effects Models* (Raudenbush & Bryk, 2002; Tranmer et al., 2014). En este diseño, las métricas topológicas extraídas en la fase descriptiva se incorporan como covariables que informan al modelo sobre la posición estructural de cada actor y concepto.

En esta metodología de análisis, la unidad base es la declaración individual (arista), que se asume no independiente, sino anidada simultáneamente, es decir, "cruzada", en dos jerarquías de nivel superior: el actor que la emite y el concepto al que hace referencia. Según la especificación final, también podrán incorporarse efectos aleatorios o fijos asociados a sesión, etapa legislativa, cámara o tipo de instancia deliberativa. Este diseño permite controlar la varianza residual generada por actores hiperactivos o por temas coyunturales de alta tracción (Tranmer et al., 2014).

Para responder a la segunda hipótesis, se estimarán modelos logísticos multinomiales donde la variable dependiente será la estrategia discursiva específica empleada. Como principales predictores se introducirán la pertenencia a la coalición discursiva, la filiación partidaria, el tipo de actor y la etapa legislativa. Para la tercera hipótesis, el análisis se enfocará en describir y modelar la adhesión general a los criterios CARIN mediante modelos logísticos multinomiales, con el objetivo de evaluar la utilidad del marco para captar patrones de merecimiento en el debate legislativo. Dado que los criterios CARIN forman parte del contenido usado para caracterizar las coaliciones, estos modelos se interpretarán con cautela y no como una prueba independiente de causalidad entre coaliciones y criterios de merecimiento.

Finalmente, para evaluar la robustez ideacional del modelo y la convergencia pragmática postulada en la cuarta hipótesis, la dimensión temporal se incorporará como tiempo discreto, principalmente mediante etapas legislativas e hitos del proceso de tramitación. Estas etapas podrán operar como efectos fijos, términos de interacción (e.g., coalición \* etapa legislativa) o, si la estructura de datos lo permite, como un nivel adicional en modelos multinivel. La estimación de probabilidades marginales predichas en distintos cortes temporales permitirá visualizar si la centroizquierda y la izquierda estructural modifican sus repertorios de justificación para asimilar los pilares del mercado tras hitos críticos, aportando evidencia sobre la resiliencia del modelo de capitalización individual frente a la crisis de legitimidad. En términos empíricos, la convergencia pragmática y la subordinación discursiva se evaluarán a partir de cambios temporales en la asociación entre coaliciones, concepciones de justicia, criterios CARIN y estrategias de legitimación. Especial atención recibirán los casos en que actores reformistas incorporen con mayor frecuencia argumentos asociados al mérito, la propiedad individual, la capitalización o la sostenibilidad financiera, o cuando las referencias a la solidaridad aparezcan articuladas con criterios contributivos, focalizados o técnicamente restringidos.

## **Referencias** {#referencias}

Anderson, K. (2018). How Have Narratives, Beliefs and Practices Shaped Pension Reform in Sweden? En R. A. W. Rhodes (Ed.), *Narrative Policy Analysis: Cases in Decentred Policy* (pp. 141–163). Springer International Publishing. https://doi.org/10.1007/978-3-319-76635-5\_7 

Arenas, A. (2010). *Historia de la Reforma Previsional Chilena: Una experiencia exitosa de política pública en democracia*. OIT. 

Ashwin, J., Chhabra, A., & Rao, V. (2025). Using Large Language Models for Qualitative Analysis can Introduce Serious Bias. *Sociological Methods & Research*, 00491241251338246\. https://doi.org/10.1177/00491241251338246 

Barozet, E. (2025). Las fluctuaciones de los modelos de justicia social de la izquierda chilena, entre las demandas de garantía de derechos y el ejercicio del poder (1990-2025). *Cahiers des Amériques latines*, (107). https://doi.org/10.4000/15qy7 

Béland, D. (2005). Ideas and Social Policy: An Institutionalist Perspective. *Social Policy & Administration*, *39*(1), 1–18. https://doi.org/10.1111/j.1467-9515.2005.00421.x 

Béland, D. (2019). Narrative stories, institutional rules, and the politics of pension policy in Canada and the United States. *Policy and Society*, *38*(3), 356–372. https://doi.org/10.1080/14494035.2019.1644071 

Béland, D., & Cox, R. H. (2016). Ideas as coalition magnets: Coalition building, policy entrepreneurs, and power relations. *Journal of European Public Policy*, *23*(3), 428–445. https://doi.org/10.1080/13501763.2015.1115533 

Béland, D., & Mandelkern, R. (2024). Ideas as explanations in social policy analysis. En *Handbook on the Political Economy of Social Policy* (pp. 39–50). Edward Elgar Publishing. https://www.elgaronline.com/edcollchap/book/9781035306497/book-part-9781035306497-9.xml 

Benavides, P., & Valdés, R. (2018). Pensiones en Chile: Antecedentes y contornos para una reforma urgente. *Centro de Políticas Públicas UC*, (N° 107). 

Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment*, *2008*(10), P10008. https://doi.org/10.1088/1742-5468/2008/10/P10008 

Blum, S. (2019). Reform narratives and argumentative coupling in German pension policy: Constructing the ‘deserving retiree’. *Policy and Society*, *38*(3), 389–407. https://doi.org/10.1080/14494035.2019.1655130 

Boltanski, L., Thévenot, L., & Porter, C. (2006). *On Justification: Economies of Worth*. Princeton University Press. https://doi.org/10.2307/j.ctv1zm2tzm 

Bonacich, P. (1987). Power and centrality: A family of measures. *American Journal of Sociology*, *92*(5), 1170–1182. https://doi.org/10.1086/228631 

Borzutzky, S. (2005). From Chicago to Santiago: Neoliberalism and Social Security Privatization in Chile. *Governance*, *18*(4), 655–674. https://doi.org/10.1111/j.1468-0491.2005.00296.x 

Borzutzky, S. (2019). You Win Some, You Lose Some: Pension Reform in Bachelet’s First and Second Administrations. *Journal of Politics in Latin America*, *11*(2), 204–230. https://doi.org/10.1177/1866802X19861491 

Bosley, M. (2025). Towards Qualitative Measurement at Scale: A Prompt-Engineering Framework for Large-Scale Analysis of Deliberative Quality in Parliamentary Debates. *Journal of Political Institutions and Political Economy*, *6*(3–4), 355–383. https://doi.org/10.1561/113.00000128 

Bril-Mascarenhas, T., & Maillet, A. (2019). How to Build and Wield Business Power: The Political Economy of Pension Regulation in Chile, 1990–2018. *Latin American Politics and Society*, *61*(1), 101–125. https://doi.org/10.1017/lap.2018.61 

Campos-Rojas, C., & González-Arias, C. (2022). Apelando a la emoción: El sistema de pensiones en el discurso de expertos económicos en la prensa chilena. *Íkala, Revista de Lenguaje y Cultura*, *27*(2), 357–374. https://doi.org/10.17533/udea.ikala.v27n2a04 

Carstensen, M. B., & Schmidt, V. A. (2016). Power through, over and in ideas: Conceptualizing ideational power in discursive institutionalism. *Journal of European Public Policy*, *23*(3), 318–337. https://doi.org/10.1080/13501763.2015.1115534 

Castiglioni, R. (2018). Determinants of Policy Change in Latin America: A Comparison of Social Security Reform in Chile and Uruguay (1973–2000). *Journal of Comparative Policy Analysis: Research and Practice*, *20*(2), 176–192. https://doi.org/10.1080/13876988.2016.1227526 

Castillo, J. C., Canales-Sellés, R., Laffert, A., & Urzúa, T. (2026). Justification trajectories for pension inequality in Chile (2016–2023): The role of social class and beliefs in meritocracy. *Frontiers in Sociology*, *11*. https://doi.org/10.3389/fsoc.2026.1771856 

Castillo, J. C., Laffert, A., Carrasco, K., & Iturra-Sanhueza, J. (2025). Perceptions of inequality and meritocracy: Their interplay in shaping preferences for market justice in Chile (2016–2023). *Frontiers in Sociology*, *10*. https://doi.org/10.3389/fsoc.2025.1634219 

Castillo, J. C., Olivos, F., & Azar, A. (2019). Deserving a Just Pension: A Factorial Survey Approach. *Social Science Quarterly*, *100*(1), 359–378. https://doi.org/10.1111/ssqu.12539 

Costa, T., & Wiggan, J. (2024). The Bolsonaro Government’s 2019 pension reform in Brazil: A policy discourse analysis. *Critical Policy Studies*, *18*(4), 620–638. https://doi.org/10.1080/19460171.2023.2289065 

Crupi, G., Tufano, R., Velasco, A., Mastropaolo, A., Poshyvanyk, D., & Bavota, G. (2025). On the Effectiveness of LLM-as-a-Judge for Code Generation and Summarization. *IEEE Transactions on Software Engineering*, *51*(8), 2329–2345. https://doi.org/10.1109/TSE.2025.3586082 

Deeming, C. (2018). The Politics of (Fractured) Solidarity: A Cross-National Analysis of the Class Bases of the Welfare State. *Social Policy & Administration*, *52*(5), 1106–1125. https://doi.org/10.1111/spol.12323 

Domínguez, D. V. (2017). *Sistema de Pensiones: Opiniones y Demandas Ciudadanas*. Espacio Público. https://espaciopublico.cl/wp-content/uploads/2021/05/Doc-Ref-N%C2%B036-Pensiones-v2.pdf 

Dunivin, Z. O. (2025). Scaling hermeneutics: A guide to qualitative coding with LLMs for reflexive content analysis. *EPJ Data Science*, *14*(1), 28\. https://doi.org/10.1140/epjds/s13688-025-00548-8 

Ebbinghaus, B., & Naumann, E. (2020). The Legitimacy of Public Pensions in an Ageing Europe: Changes in Subjective Evaluations and Policy Preferences, 2008–2016. En *Welfare State Legitimacy in Times of Crisis and Austerity* (pp. 159–176). Edward Elgar Publishing. https://www.elgaronline.com/edcollchap/edcoll/9781788976299/9781788976299.00020.xml 

Ebbinghaus, B., & Wiß, T. (2024). The political economy of pension policy. En *Handbook on the Political Economy of Social Policy* (pp. 190–202). Edward Elgar Publishing. https://www.elgaronline.com/edcollchap/book/9781035306497/book-part-9781035306497-23.xml 

Esping-Andersen, G. (1990). *The Three Worlds of Welfare Capitalism*. Princeton University Press. 

Ferre, J. C. (2023). Welfare regimes in twenty-first-century Latin America. *Journal of International and Comparative Social Policy*, *39*(2), 101–127. https://doi.org/10.1017/ics.2023.16 

Fourcade, M., & Healy, K. (2007). Moral Views of Market Society. *Annual Review of Sociology*, *33*(Volume 33, 2007), 285–311. https://doi.org/10.1146/annurev.soc.33.040406.131642 

Freeman, L. C. (1977). A Set of Measures of Centrality Based on Betweenness. *Sociometry*, *40*(1), 35–41. https://doi.org/10.2307/3033543 

Gaffney, S. (2025). The ‘pathologically state dependent’ versus ‘middle-aged ministers on mammoth salaries’: The legitimation contest over a 2013 austerity measure in the Republic of Ireland. *Discourse & Society*, *36*(2), 180–195. https://doi.org/10.1177/09579265241266020 

Garber, C. (2021). Continuidad neoliberal ví­a tecnocracia: Las comisiones asesoras presidenciales para la reforma previsional en Chile. *Revista Temas Sociológicos*, (28), 473–508. https://doi.org/10.29344/07196458.28.2431 

Godoy, S. M. (2023). Breve análisis del proceso actual de reforma al sistema de pensiones en Chile: Una mirada crítica. *OBSERVATORIO DE FINANCIAMIENTO PARA EL DESARROLLO*, (4), 14–22. 

González Arias, C., & Campos Rojas, C. (2020). El flujo de opinión sobre el sistema de pensiones en cuatro géneros de la prensa chilena: Cobertura, voces y problemáticas. *Logos (La Serena)*, *30*(1), 138–153. https://doi.org/10.15443/rl3012 

Hagelund, A., & Grødem, A. S. (2019). When metaphors become cognitive locks: Occupational pension reform in Norway. *Policy and Society*, *38*(3), 373–388. https://doi.org/10.1080/14494035.2019.1646070 

Hajer, M. A. (1997). Discourse Analysis. En M. A. Hajer (Ed.), *The Politics of Environmental Discourse: Ecological Modernization and the Policy Process* (p. 0). Oxford University Press. https://doi.org/10.1093/019829333X.003.0003 

Hayes, A. S. (2025). “Conversing” With Qualitative Data: Enhancing Qualitative Research Through Large Language Models (LLMs). *International Journal of Qualitative Methods*, *24*, 16094069251322346\. https://doi.org/10.1177/16094069251322346 

Hill, C., Dahil, A., Simpson, G., Hardisty, D., Keast, J., Pinn, C. K., & Dambha-Miller, H. (2026). Large language models for thematic analysis in healthcare research: A blinded mixed-methods comparison with human analysts. *PLOS Digital Health*, *5*(4), e0001189. https://doi.org/10.1371/journal.pdig.0001189 

Hilmar, T. (2025). Who deserves economic relief? Examining Twitter/X debates about Covid-19 economic relief for small businesses and the self-employed in Germany. *Journal of Social Policy*, *54*(4), 1153–1169. https://doi.org/10.1017/S0047279424000096 

Kay, S. J., & Borzutzky, S. (2022). Can defined contribution pensions survive the pandemic? The Chilean case. *International Social Security Review*, *75*(1), 31–50. https://doi.org/10.1111/issr.12286 

Knotz, C. M., Gandenberger, M. K., Fossati, F., & Bonoli, G. (2022). A Recast Framework for Welfare Deservingness Perceptions. *Social Indicators Research*, *159*(3), 927–943. https://doi.org/10.1007/s11205-021-02774-9 

Kohli, M. (1987). Retirement and the moral economy: An historical interpretation of the German case. *Journal of Aging Studies*, *1*(2), 125–144. https://doi.org/10.1016/0890-4065(87)90003-X 

Kristjánsson, T. Ó., Henriksen, A. F., Hansen, M. L., Kovacs, D. G., & Bjerrum, A. (2026). Prompting large language models and evaluating inter- and intra-rater agreement for cancer progression assessment from radiology reports. *ESMO Real World Data and Digital Oncology*, *11*, 100689\. https://doi.org/10.1016/j.esmorw.2026.100689 

Kuhlmann, J., & Blum, S. (2022). Sozialpolitische Erzählungen – Ein Vergleich narrativer Strategien in der Finanzkrise und der Corona-Krise. *Zeitschrift für Politikwissenschaft*, *32*(1), 117–140. https://doi.org/10.1007/s41358-022-00311-9 

Laenen, T., Rossetti, F., & van Oorschot, W. (2019). Why deservingness theory needs qualitative research: Comparing focus group discussions on social welfare in three welfare regimes. *International Journal of Comparative Sociology*, *60*(3), 190–216. https://doi.org/10.1177/0020715219837745 

Lane, R. E. (1986). Market Justice, Political Justice. *American Political Science Review*, *80*(2), 383–402. https://doi.org/10.2307/1958264 

Larrañaga, O. (2024). *Avances y Obstaculos en el sistema de pensiones en Chile (1980-2023)* (N°. 48; Documentos de Política Pública). PNUD América Latina y el Caribe. https://www.undp.org/es/latin-america/publicaciones/avances-y-obstaculos-en-el-sistema-de-pensiones-en-chile-1980-2023 

Lee, H. B., & Kim, D.-E. (2026). Policy experts’ strategy in deliberative polling on Korean pension reform: Utilizing valence and polysemic ideas through framing and narrative strategies. *Critical Policy Studies*, *0*(0), 1–25. https://doi.org/10.1080/19460171.2026.2655672 

Leifeld, P. (2013). Reconceptualizing Major Policy Change in the Advocacy Coalition Framework: A Discourse Network Analysis of German Pension Politics. *Policy Studies Journal*, *41*(1), 169–198. https://doi.org/10.1111/psj.12007 

Leifeld, P. (2017). Discourse Network Analysis: Policy Debates as Dynamic Networks. En J. N. Victor, A. H. Montgomery, & M. Lubell (Eds.), *The Oxford Handbook of Political Networks* (p. 0). Oxford University Press. https://doi.org/10.1093/oxfordhb/9780190228217.013.25 

Leifeld, P. (2020). Policy Debates and Discourse Network Analysis: A Research Agenda. *Politics and Governance*, *8*(2), 180–183. 

Lemke, J. L. (2012). Technical discourse and Technocratic Ideology. En *Learning, Keeping and Using Language* (pp. 435–460). John Benjamins Publishing Company. https://doi.org/https://doi.org/10.1075/z.lkul2.31lem 

Liebig, S., & Sauer, C. (2016). Sociology of Justice. En C. Sabbagh & M. Schmitt (Eds.), *Handbook of Social Justice Theory and Research* (pp. 37–59). Springer. https://doi.org/10.1007/978-1-4939-3216-0\_3 

López-González, L., & Vélez-Maya, M. M. (2025). Memorias políticas y acción colectiva: Usos políticos del pasado en el movimiento NO \+ AFP en Chile. *Revista Austral de Ciencias Sociales*, (48), 317–335. https://doi.org/10.4206/rev.austral.cienc.soc.2025.n48-16 

Lusher, D., Koskinen, J., & Robins, G. (Eds.). (2013). *Exponential Random Graph Models for Social Networks: Theory, Methods, and Applications*. Cambridge University Press. https://doi.org/10.1017/CBO9780511894701 

Madariaga, A. (2020). The three pillars of neoliberalism: Chile’s economic policy trajectory in comparative perspective. *Contemporary Politics*, *26*(3), 308–329. https://doi.org/10.1080/13569775.2020.1735021 

Martin, M. P., & Alfaro, J. (2017). POLÍTICAS DE BIENESTAR EN CONTEXTOS NEOLIBERALES: Tensiones del modelo chileno. *Caderno CRH*, *30*, 137–155. https://doi.org/https://doi.org/10.1590/S0103-49792017000100009 

Matus, F. (2020). Formas de Representación de la Participación Política Digital: El caso del conflicto por el Sistema de Pensiones Chileno (2016-2017). *RevIISE: Revista de Ciencias Sociales y Humanas*, *15*(15), 199–217. 

Mesa-Lago, C., & Bertranou, F. (2016). Pension reforms in Chile and social security principles, 1981–2015. *International Social Security Review*, *69*(1), 25–45. https://doi.org/10.1111/issr.12093 

Meuleman, B., Roosma, F., & Abts, K. (2020). Welfare deservingness opinions from heuristic to measurable concept: The CARIN deservingness principles scale. *Social Science Research*, *85*, 102352\. https://doi.org/10.1016/j.ssresearch.2019.102352 

Michoń, P. (2021). Deservingness for “Family 500 +” Benefit in Poland: Qualitative Study of Internet    Debates. *Social Indicators Research*, *157*(1), 203–223. https://doi.org/10.1007/s11205-021-02655-1 

Migone, A., Howlett, M., & Howlett, A. (2024). Paradigmatic stability, ideational robustness, and policy persistence: Exploring the impact of policy ideas on policy-making. *Policy and Society*, *43*(2), 189–203. https://doi.org/10.1093/polsoc/puae004 

Mishra, V., Lurie, Y., & Mark, S. (2025). Accuracy of LLMs in medical education: Evidence from a concordance test with medical teacher. *BMC Medical Education*, *25*(1), 443\. https://doi.org/10.1186/s12909-025-07009-w 

Misra, R., Dahal, R., Kirk, B., Khan, R., Dogan, G., Chataut, R., & Gyawali, P. (2026). Large Language Models in Qualitative Analysis: Comparing Traditional and Researcher-Interpreted Approaches. *International Journal of Qualitative Methods*, *25*, 16094069261426100\. https://doi.org/10.1177/16094069261426100 

Mulligan, E., Nally, B. M., van den Heuvel \- Warren, J., & Bassey, E. (2026). Cognitive and normative discourse in EU approach to policy reform: The case of pensions. *Journal of European Social Policy*, 09589287261419987\. https://doi.org/10.1177/09589287261419987 

Mustafa, A., Naseem, U., & Rahimi Azghadi, M. (2026). Can reasoning LLMs enhance clinical document classification? *Health and Technology*, *16*(3), 387–400. https://doi.org/10.1007/s12553-025-01041-y 

Parada-Contzen, M. (2023). Gender, family status and health characteristics: Understanding retirement inequalities in the Chilean pension model. *International Labour Review*, *162*(2), 271–303. https://doi.org/10.1111/ilr.12365 

Parada-Contzen, M., & Sanhueza, I. (2025). On the Evolution of Population Preferences toward Retirement System Design and Savings Withdrawal: Evidence from Chile. *The Journal of Retirement*, *12*(3), 68–90. https://doi.org/10.3905/jor.2024.1.167 

Peters, B. G., Pierre, J., & King, D. S. (2005). The Politics of Path Dependency: Political Conflict in Historical Institutionalism. *Journal of Politics*, *67*(4), 1275–1300. https://doi.org/10.1111/j.1468-2508.2005.00360.x 

Randerson, S., Graydon-Guy, T., Lin, E.-Y., & Casswell, S. (2025). Exploring the Use of a Large Language Model for Inductive Content Analysis in a Discourse Network Analysis Study. *Social Science Computer Review*, 08944393251326175\. https://doi.org/10.1177/08944393251326175 

Raudenbush, S. W., & Bryk, A. S. (2002). *Hierarchical Linear Models: Applications and Data Analysis Methods*. SAGE. 

Reeskens, T., & van Oorschot, W. (2013). Equity, equality, or need? A study of popular preferences for welfare redistribution principles across 24 European countries. *Journal of European Public Policy*, *20*(8), 1174–1195. https://doi.org/10.1080/13501763.2012.752064 

Ring, P., Ervik, R., & Lindén, T. S. (2020). Justifying pension reforms: Comparing policy discourses in Norway and the UK. *European Journal of Social Security*, *22*(3), 306–326. https://doi.org/10.1177/1388262720950736 

Román Brugnoli, J. A., & Osorio Gonnet, C. (2015). Solidaridad y políticas públicas en el discurso de los gobiernos de la Concertación en Chile. *Revista Electrónica de Psicología Política*, *13*(35), 39\. 

Rozas, J., & Maillet, A. (2019). Entre marchas, plebiscitos e iniciativas de ley: Innovación en el repertorio de estrategias del movimiento No Más AFP en Chile (2014-2018). *Izquierdas*, (48), 1–21. 

Rozas-Bugueño, J., & Maillet, A. (2024). Challenging the policy space: The legitimation of alternatives in Chilean pension policy (1980–2019). *Latin American Policy*, *15*(2), 235–254. https://doi.org/10.1111/lamp.12343 

Sachweh, P. (2016). Social Justice and the Welfare State: Institutions, Outcomes, and Attitudes in Comparative Perspective. En C. Sabbagh & M. Schmitt (Eds.), *Handbook of Social Justice Theory and Research* (pp. 293–313). Springer. https://doi.org/10.1007/978-1-4939-3216-0\_16 

Sachweh, P., Ullrich, C. G., & Christoph, B. (2006). Die Gesellschaftliche Akzeptanz der Sozialhilfe. *KZfSS Kölner Zeitschrift für Soziologie und Sozialpsychologie*, *58*(3), 489–509. https://doi.org/10.1007/s11575-006-0107-5 

Schmidt, V. A. (2002). Does Discourse Matter in the Politics of Welfare State Adjustment? *Comparative Political Studies*, *35*(2), 168–193. https://doi.org/10.1177/0010414002035002002 

Schmidt, V. A. (2008). Discursive Institutionalism: The Explanatory Power of Ideas and Discourse. *Annual Review of Political Science*, *11*(Volume 11, 2008), 303–326. https://doi.org/10.1146/annurev.polisci.11.060606.135342 

Schmidt, V. A. (2016). The roots of neo-liberal resilience: Explaining continuity and change in background ideas in Europe’s political economy. *The British Journal of Politics and International Relations*, *18*(2), 318–334. https://doi.org/10.1177/1369148115612792 

Silva, P. (2006). LOS TECNÓCRATAS Y LA POLÍTICA EN CHILE: PASADO Y PRESENTE. *Revista de ciencia política (Santiago)*, *26*(2), 175–190. https://doi.org/10.4067/S0718-090X2006000200010 

Siviş, S. (2022). Who is (un)deserving? Differential healthcare access and the interplay between social and symbolic boundary-drawing towards Syrian refugees in Turkey. *Journal of Ethnic and Migration Studies*, *48*(17), 4029–4048. https://doi.org/10.1080/1369183X.2022.2058470 

Soemer, K., Grunow, D., & Eger, S. (2025, octubre 6). *Social sciences and AI joining forces: Towards new approaches for computational social sciences*. First Workshop on Bridging NLP and Public Opinion Research. https://openreview.net/forum?id=fR4KyaDICs 

Summers, K., Edmiston, D., Geiger, B. B., Ingold, J., Scullion, L., de Vries, R., & Young, D. (2025). Claiming deservingness: The durability of social security claimant discourses during the Covid-19 pandemic. *The Sociological Review*, 00380261251336544\. https://doi.org/10.1177/00380261251336544 

Taylor-Gooby, P., Hvinden, B., Mau, S., Leruth, B., Schoyen, M. A., & Gyory, A. (2019). Moral economies of the welfare state: A qualitative comparative study. *Acta Sociologica*, *62*(2), 119–134. https://doi.org/10.1177/0001699318774835 

Theiss, M. (2023). How Does the Content of Deservingness Criteria Differ for More and Less Deserving Target Groups? An Analysis of Polish Online Debates on Refugees and Families with Children. *Journal of Social Policy*, *52*(4), 962–980. https://doi.org/10.1017/S0047279422000058 

Tortola, P. D. (2020). Technocracy and depoliticization. En *The Technocratic Challenge to Democracy*. Routledge. 

Traag, V. A., Waltman, L., & van Eck, N. J. (2019). From Louvain to Leiden: Guaranteeing well-connected communities. *Scientific Reports*, *9*(1), 5233\. https://doi.org/10.1038/s41598-019-41695-z 

Tranmer, M., Steel, D., & Browne, W. J. (2014). Multiple-Membership Multiple-Classification Models for Social Network and Group Dependences. *Journal of the Royal Statistical Society Series A: Statistics in Society*, *177*(2), 439–455. https://doi.org/10.1111/rssa.12021 

Väänänen, N., & Liukko, J. (2022). Justifying a financially and socially sustainable pension reform: A comparative study of Finland and France. *International Journal of Sociology and Social Policy*, *43*(5–6), 507–520. https://doi.org/10.1108/IJSSP-04-2022-0091 

Vaara, E., Tienari, J., & Laurila, J. (2006). Pulp and Paper Fiction: On the Discursive Legitimation of Global Industrial Restructuring. *Organization Studies*, *27*(6), 789–813. https://doi.org/10.1177/0170840606061071 

Van Hootegem, A., Meuleman, B., & Abts, K. (2024). Two faces of benefit generosity: Comparing justice preferences in the access to and level of welfare benefits. *European Sociological Review*, *40*(3), 523–534. https://doi.org/10.1093/esr/jcad053 

Van Leeuwen, T. (2007). Legitimation in discourse and communication. *Discourse & Communication*, *1*(1), 91–112. https://doi.org/10.1177/1750481307071986 

van Oorschot, W. (2000). Who should get what, and why? On deservingness criteria and the conditionality of solidarity among the public. *Policy & Politics*, *28*(1), 33–48. https://doi.org/10.1332/0305573002500811 

van Oorschot, W. (2006). Making the difference in social Europe: Deservingness perceptions among                citizens of European welfare states. *Journal of European Social Policy*, *16*(1), 23–42. https://doi.org/10.1177/0958928706059829 

van Oorschot, W., Laenen, T., Roosma, F., & Meuleman, B. (2022). Recent advances in understanding welfare attitudes in Europe. En *Social Policy in Changing European Societies* (pp. 202–217). Edward Elgar Publishing. https://www.elgaronline.com/edcollchap-oa/book/9781802201710/book-part-9781802201710-21.xml 

Vela, J. (2025). El Sistema de Pensiones chileno posreforma 2025: ¿cuánto queda de neoliberalismo? *Estudios Públicos*, 1–45. https://doi.org/10.38178/07183089/1157240905 

Wiggan, J. (2012). Telling stories of 21st century welfare: The UK Coalition government and the neo-liberal discourse of worklessness and dependency. *Critical Social Policy*, *32*(3), 383–405. https://doi.org/10.1177/0261018312444413 

Wiß, T., Fernández, J. J., & Anderson, K. M. (2025). Attitudes towards the public-private mix for retirement income in Europe. *Journal of European Social Policy*, 09589287251345904\. https://doi.org/10.1177/09589287251345904 

Woelfle, T., Hirt, J., Janiaud, P., Kappos, L., Ioannidis, J. P. A., & Hemkens, L. G. (2024). Benchmarking Human–AI collaboration for common evidence appraisal tools. *Journal of Clinical Epidemiology*, *175*, 111533\. https://doi.org/10.1016/j.jclinepi.2024.111533 

Zhang, Z., Ge, L., Hu, R., & Wang, Y. (2026). A zero-shot prompt learning approach on fine-grained text classification. *Scientific Reports*, *16*(1), 5260\. https://doi.org/10.1038/s41598-025-34825-3 

[^1]:  Las categorías nuevas generadas por el modelo serán analizadas para encontrar puntos de mejora en el libro de códigos y los prompts.

[^2]:  Técnica que consiste en proporcionar una muestra de ejemplos iniciales a clasificadores para realizar inferencia.