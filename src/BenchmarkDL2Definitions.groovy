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
  new File("data/go.owl"))
OWLDataFactory dataFactory = manager.getOWLDataFactory()
ConsoleProgressMonitor progressMonitor = new ConsoleProgressMonitor()
OWLReasonerConfiguration config = new SimpleConfiguration(progressMonitor)
ElkReasonerFactory reasonerFactory = new ElkReasonerFactory()

def df = dataFactory 
def shortFormProvider = new LabelShortFormProvider(ont.getImportsClosure())
def renderer = new ManchesterOWLSyntaxOWLObjectRendererImpl()
renderer.setShortFormProvider(shortFormProvider)

def getName = { cl ->
  return shortFormProvider.getShortForm(cl);
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
    new BufferedWriter(new FileWriter("data/benchmarkDL2Definitions_go.txt")))


ont.getClassesInSignature(true).each { cl ->
    clName = getName(cl)
    EntitySearcher.getEquivalentClasses(cl, ont).each { cExpr ->
      if (!cExpr.isClassExpressionLiteral()) {
        String dl = renderer.render(cExpr);
        EntitySearcher.getAnnotations(cl, ont).each { annotation  ->
          def aProp = annotation.getProperty()
          if (aProp in definitions) {
             if (annotation.getValue() instanceof OWLLiteral) {
                String definition = annotation.getValue().getLiteral();
                //out.print("CLASS name:" + clName + "\tdl:" + dl + "\tdef:" + definition + "\n");
                out.print(clName + "\t" + dl + "\t" + definition + "\n");
             }
          }
        }
      }   
    }
}

out.flush()
out.close()
