# Decisiones teóricas y operacionales del libro de códigos v0.3.0

## Objeto de codificación

La versión 0.2 adopta la variante de análisis de redes discursivas orientada a *discourse coalitions*. Leifeld distingue esta estrategia de la operacionalización de *advocacy coalitions*. La segunda codifica posiciones sobre instrumentos de política; la primera codifica justificaciones o narrativas utilizadas para sostener una posición respecto de un asunto [@leifeld_discourse_2017]. En consecuencia, el libro incluye razones normativas y excluye preferencias instrumentales que carecen de una justificación expresada.

La unidad empírica sigue siendo una declaración contenida en el bloque objetivo. El bloque reúne uno o más párrafos de una misma intervención cuando el primero tiene menos de 50 palabras. En ese caso se agregan párrafos siguientes hasta alcanzar 100 palabras o terminar la intervención. Los bloques anterior y siguiente permiten identificar la conclusión política a la que se aplica la razón. La selección anotada debe contener la justificación. Por ejemplo, una petición de aumentar una pensión carece por sí misma de criterio codificable. La referencia a privación material permite codificar necesidad; una apelación al derecho de todas las personas permite codificar igualdad o universalismo.

## Integración de CARIN y los criterios contextuales

Laenen et al. aplican análisis de contenido dirigido con cinco criterios CARIN definidos a priori: control, actitud, reciprocidad, identidad y necesidad. El procedimiento admite códigos emergentes y exige tres componentes para codificar una declaración: una afirmación de justicia, una prestación o servicio de bienestar y una justificación acerca de su otorgamiento. El análisis identifica además igualdad o universalismo, conciencia de costos e inversión social como criterios contextuales. Estos criterios remiten a la sociedad o al sistema de bienestar, mientras CARIN evalúa características de la población destinataria [@laenen_why_2019].

La v0.3.0 incorpora los cinco criterios CARIN y dos criterios contextuales. Igualdad o universalismo cubre acceso, cobertura, trato o nivel de protección cuando una regla igualitaria justifica el diseño. Conciencia de costos se operacionaliza como restricción de gasto: los costos fiscales o administrativos, la escasez de recursos o la falta de viabilidad financiera justifican rechazar, limitar, reducir, postergar o focalizar una reforma o expansión previsional. Inversión social permanece fuera de esta versión porque el estudio de Laenen et al. la encontró únicamente en uno de sus contextos nacionales y las rondas chilenas no produjeron un candidato equivalente.

La proposición ancla de conciencia de costos afirma que la reforma o expansión evaluada es demasiado costosa, carece de financiamiento sostenible o excede la capacidad fiscal estatal. `Apoyo` registra la afirmación de esa restricción. `Rechazo` registra su refutación, por ejemplo cuando un actor sostiene que la reforma es sostenible, está financiada adecuadamente o cabe dentro de la capacidad fiscal. La orientación negativa y asimétrica es deliberada y debe conservarse al interpretar la red.

La referencia a la sostenibilidad financiera presente o futura puede expresar conciencia de costos aunque el actor no cuantifique el monto ni describa el mecanismo fiscal. La regla exige que la sostenibilidad funcione como razón para limitar, rechazar o defender la reforma. Por esta razón, una afirmación de que el sistema futuro sería financieramente insostenible se codifica como `Apoyo`; una afirmación de que la reforma sí es sostenible se codifica como `Rechazo`.

La codificación múltiple está permitida. Una propuesta universal puede invocar simultáneamente igualdad y necesidad; un argumento contra una transferencia puede combinar propiedad individual e ineficiencia estatal. Cada código debe corresponder a una justificación reconocible en el texto.

## Conceptos específicos del caso

`capitalizacion_individual` se reincorpora con un alcance acotado y codifica la regla según la cual las cotizaciones ingresan a cuentas individuales para financiar la pensión de su titular. Incluye defensas del destino individual de todas o la mayor parte de las cotizaciones, afirmaciones de que cada persona debe financiar su propia pensión mediante ahorro previsional y críticas explícitas a ese arreglo porque produce pensiones insuficientes o reproduce desigualdades. La mención descriptiva al sistema AFP continúa fuera del código.

La función de la afirmación establece la frontera con reciprocidad contributiva: capitalización individual responde qué ocurre con las cotizaciones y quién financia la pensión; reciprocidad define qué beneficio, cuantía o prioridad se justifica por aportes o trabajo previos. Por ello, el destino del aporte en la cuenta propia corresponde a capitalización, mientras la relación entre mayor cotización y mayor beneficio corresponde a reciprocidad. Ambas pueden coexistir cuando el texto formula las dos reglas.

Propiedad individual de los fondos permanece como concepto específico. Su vínculo con *entitlement* se registra como una inferencia del estudio. Hülle et al. definen *entitlement* como asignación basada en características adscritas o en un estatus adquirido previamente [@hulle_measuring_2018]. El saldo acumulado puede interpretarse como un estatus adquirido que fundamenta un título sobre los recursos. La v0.3 conserva el concepto empírico y posterga su agregación bajo una familia general de *entitlement*.

La v0.3.0 mantiene solidaridad como solidaridad intergeneracional. El criterio afirma una responsabilidad compartida entre cohortes y se aplica cuando esa relación justifica transferir recursos o distribuir riesgos entre generaciones activas y jubiladas. Incluye cotizaciones o aportes presentes destinados a financiar pensiones actuales, fondos comunes defendidos mediante una responsabilidad entre generaciones y mecanismos que distribuyen riesgos de longevidad, demográficos o financieros entre cohortes. También incluye el rechazo explícito de esas transferencias; la orientación registra desacuerdo con la proposición ancla.

Esta delimitación separa el criterio de igualdad o universalismo. Igualdad o universalismo establece quién debe recibir protección y bajo qué regla de acceso, trato o cobertura. Solidaridad intergeneracional establece qué generaciones deben financiar o asumir los riesgos previsionales de otras. Una declaración puede recibir ambos códigos cuando formula una regla universal y también identifica una relación de financiamiento entre cohortes.

Las transferencias entre personas de distintos ingresos dentro de una misma generación se asignan según la justificación expresada, por ejemplo necesidad, igualdad o reciprocidad. Las compensaciones de género, cuidados o lagunas previsionales siguen la misma regla. El uso retórico de solidaridad y la mención de un fondo común quedan excluidos cuando el texto no identifica una relación intergeneracional.

`prevision_como_mercado` reúne argumentos sobre la legitimidad de organizar la protección previsional mediante competencia, inversión financiera, rentabilidad privada, lucro e incentivos de mercado. `Apoyo` registra defensas de esos mecanismos. También registra afirmaciones de que un beneficio social o redistributivo debilita el trabajo, la productividad, el ahorro o la formalización, porque el efecto conductual funciona como justificación de incentivos de mercado. `Rechazo` cubre críticas a la previsión como negocio, a la primacía de intereses empresariales sobre el derecho social y a la captura del sistema por actores privados.

Las comisiones se integran en este código cuando se califican como abusivas, excesivas o como extracción injustificada de los recursos de los cotizantes. Un monto o porcentaje descriptivo queda fuera. Esta regla evita mantener un código separado para una manifestación específica de una crítica más amplia a la mercantilización.

`ilegitimidad_origen_dictatorial` registra la línea argumental según la cual el origen autoritario, coercitivo o engañoso del sistema AFP debilita su legitimidad actual. Incluye la imposición sin deliberación democrática, la incorporación forzada o engañosa de trabajadores y las promesas fundacionales incumplidas cuando se conectan con ese origen. Una fecha histórica aislada y una crítica contemporánea al desempeño de las AFP quedan fuera.

La v0.3.0 no incorpora un código de progresividad tributaria. El caso observado es poco frecuente y puede conservarse mediante nota o `Revisar` si vuelve a aparecer. Esta decisión evita ampliar igualdad o universalismo a una regla de distribución de cargas que todavía carece de recurrencia empírica.

## Ineficiencia estatal como justificación normativa

`ineficiencia_estado` combina una premisa cognitiva con una consecuencia normativa. La premisa atribuye al Estado incapacidad, ineficiencia, uso político, apropiación, dilapidación o riesgo de pérdida. La consecuencia afirma que el resguardo legítimo de las cotizaciones exige limitar o rechazar la administración estatal. El código incluye también refutaciones explícitas, como la defensa de una gestión pública profesional, transparente o segura; la orientación registra si el actor afirma o rechaza la proposición ancla.

Esta decisión establece una regla general para futuros conceptos cognitivos. Una afirmación sobre el funcionamiento del mundo entra en la red cuando el hablante la usa como razón para aceptar o rechazar una distribución, derecho o diseño previsional. Una descripción institucional aislada queda fuera. La posible codificación paralela de premisas cognitivas puede desarrollarse como una segunda capa analítica después del pilotaje, con variables y redes separadas para evitar mezclar razones normativas con diagnósticos causales.

## Estrategia inductiva

La opción `Revisar` registra justificaciones normativas explícitas que el esquema no cubre. Cada propuesta debe conservar el span, un nombre tentativo y una nota que explique la regla distributiva o institucional expresada. Después de la ronda se agrupan propuestas semánticamente próximas y se evalúan tres condiciones: recurrencia en más de una declaración, frontera operacional distinguible y relevancia para las coaliciones discursivas. Los candidatos aceptados se incorporan a una versión nueva; los diagnósticos factuales permanecen fuera del libro normativo.

Los votos, asistencias y pasajes procedimentales permanecen en la muestra cuando el corpus los contiene. Si carecen de una declaración sustantiva, se marcan como `Sin declaraciones codificables` y reciben la flag `Voto` o `Procedimental`. El comentario general permite registrar problemas de brevedad, truncamiento, contexto o segmentación sin convertirlos en conceptos de la red discursiva.

## Preguntas para la siguiente iteración

La siguiente ronda permitirá evaluar si igualdad y universalismo requieren códigos separados y si las premisas cognitivas recurrentes justifican una capa adicional vinculada con los conceptos normativos. También permitirá comprobar la frontera entre capitalización y reciprocidad, la amplitud de previsión como mercado, la aplicación de conciencia de costos sin cuantificación y la recurrencia de la ilegitimidad del origen dictatorial.
