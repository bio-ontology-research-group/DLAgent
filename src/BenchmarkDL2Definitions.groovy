@Grapes([
  @Grab(group='org.semanticweb.elk', module='elk-owlapi', version='0.4.2'),
  @Grab(group='net.sourceforge.owlapi', module='owlapi-api', version='4.1.0'),
  @Grab(group='net.sourceforge.owlapi', module='owlapi-apibinding', version='4.1.0'),
  @Grab(group='net.sourceforge.owlapi', module='owlapi-impl', version='4.1.0'),
  @Grab(group='net.sourceforge.owlapi', module='owlapi-parsers', version='4.1.0'),
  @GrabConfig(systemClassLoader=true)
  ])
package src
import org.semanticweb.owlapi.model.parameters.*
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.reasoner.*
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.io.*;
import org.semanticweb.owlapi.owllink.*;
import org.semanticweb.owlapi.util.*;
import org.semanticweb.owlapi.search.*;
import org.semanticweb.elk.owlapi.ElkReasonerFactory;
import org.semanticweb.elk.owlapi.ElkReasonerConfiguration
import org.semanticweb.elk.reasoner.config.*
import org.semanticweb.owlapi.manchestersyntax.renderer.*
import org.semanticweb.owlapi.formats.*
import src.LabelShortFormProvider
OWLOntologyManager manager = OWLManager.createOWLOntologyManager()
OWLOntology ont = manager.loadOntologyFromOntologyDocument(
  new File("/home/nur/workspace/BH25/DLAgent/data/hp.owl"))
OWLDataFactory dataFactory = manager.getOWLDataFactory()
ConsoleProgressMonitor progressMonitor = new ConsoleProgressMonitor()
OWLReasonerConfiguration config = new SimpleConfiguration(progressMonitor)
ElkReasonerFactory reasonerFactory = new ElkReasonerFactory()
def df = dataFactory
def shortFormProvider = new LabelShortFormProvider(ont.getImportsClosure())
def renderer = new ManchesterOWLSyntaxOWLObjectRendererImpl()
renderer.setShortFormProvider(shortFormProvider)
def getName = { cl ->
  // Try to get English label first
  def englishLabel = null
  EntitySearcher.getAnnotations(cl, ont).each { annotation ->
    if (annotation.getProperty().isLabel()) {
      if (annotation.getValue() instanceof OWLLiteral) {
        def literal = annotation.getValue() as OWLLiteral
        def lang = literal.getLang()
        if (lang == null || lang.isEmpty() || lang == "en") {
          englishLabel = literal.getLiteral()
        }
      }
    }
  }
  
  // If no English label found, fall back to short form
  return englishLabel ?: shortFormProvider.getShortForm(cl)
}
// Description properties
def definitions = [
	df.getOWLAnnotationProperty(new IRI('http://purl.obolibrary.org/obo/IAO_0000115')),
	df.getOWLAnnotationProperty(new IRI('http://www.w3.org/2004/02/skos/core#definition')),
	df.getOWLAnnotationProperty(new IRI('http://purl.org/dc/elements/1.1/description')),
	df.getOWLAnnotationProperty(new IRI('http://purl.org/dc/terms/description')),
	df.getOWLAnnotationProperty(new IRI('http://www.geneontology.org/formats/oboInOwl#hasDefinition'))
    ]
out = new PrintWriter(
    new BufferedWriter(new FileWriter("/home/nur/workspace/BH25/DLAgent/data/benchmarkDL2Definitions_hp.txt")))
ont.getClassesInSignature(true).each { cl ->
    clName = getName(cl)
    
    // Get the first English definition for this class
    def englishDefinition = null
    EntitySearcher.getAnnotations(cl, ont).each { annotation ->
      def aProp = annotation.getProperty()
      if (aProp in definitions) {
         if (annotation.getValue() instanceof OWLLiteral) {
            def literal = annotation.getValue() as OWLLiteral
            def lang = literal.getLang()
            // Only include English definitions (empty lang, null lang, or "en")
            if (lang == null || lang.isEmpty() || lang == "en") {
              if (englishDefinition == null) {
                englishDefinition = literal.getLiteral();
              }
            }
         }
      }
    }
    
    // Get the first non-literal equivalent class expression
    def dlExpression = null
    EntitySearcher.getEquivalentClasses(cl, ont).each { cExpr ->
      if (!cExpr.isClassExpressionLiteral()) {
        if (dlExpression == null) {
          dlExpression = renderer.render(cExpr);
        }
      }
    }
    
    // Print one line per class with English label, one definition, and one DL expression
    if (clName && dlExpression && englishDefinition) {
      out.print("CLASS name:" + clName + "\tdl:" + (dlExpression ?: "") + "\tdef:" + (englishDefinition ?: "") + "\n");
}
}
out.flush()
out.close()
