package nl.infrabim.kip.notion.person;

import com.netflix.graphql.dgs.DgsComponent;
import com.netflix.graphql.dgs.DgsMutation;
import com.netflix.graphql.dgs.DgsQuery;
import com.netflix.graphql.dgs.InputArgument;
import com.netflix.dgs.codegen.generated.types.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@DgsComponent
public class PersonDataFetcher {

    static Map<String, Person> persons = new HashMap<>();

    @DgsQuery
    public Boolean isConcept(@InputArgument String personId, @InputArgument DerivedConcept concept) {
        Person person = persons.get(personId);
        if (person == null) {
            return false;
        }
        return checkConcept(person, concept);
    }

    private boolean checkConcept(Person person, DerivedConcept concept) {
        for (View view : person.getViews()) {
            String viewName = view.getName();
            switch (viewName) {
                case "Legal View" -> {
                    LegalView legalView = (LegalView) view;
                    switch (concept) {
                        case LEGAL_ADULT -> {
                            return legalView.getLegalAge() >= 18;
                        }
                        case LEGAL_BOY -> {
                            return legalView.getLegalAge() < 18 && legalView.getLegalGender().equals(LegalGender.M);
                        }
                        case LEGAL_CHILD -> {
                            return legalView.getLegalAge() < 18;
                        }
                        case LEGAL_FEMALE -> {
                            return legalView.getLegalGender().equals(LegalGender.F);
                        }
                        case LEGAL_GIRL -> {
                            return legalView.getLegalAge() < 18 && legalView.getLegalGender().equals(LegalGender.F);
                        }
                        case LEGAL_MALE -> {
                            return legalView.getLegalGender().equals(LegalGender.M);
                        }
                        case LEGAL_MAN -> {
                            return legalView.getLegalAge() >= 18 && legalView.getLegalGender().equals(LegalGender.M);
                        }
                        case PERSON -> {
                            return true;
                        }
                        case LEGAL_WOMAN -> {
                            return legalView.getLegalAge() >= 18 && legalView.getLegalGender().equals(LegalGender.F);
                        }
                    }
                }
                case "Biomedical View" -> {
                    BiomedicalView biomedicalView = (BiomedicalView) view;
                    switch (concept) {
                        case BIOMEDICAL_ADULT -> {
                            return biomedicalView.getBiomedicalAge() >= 18;
                        }
                        case BIOMEDICAL_BOY -> {
                            return biomedicalView.getBiomedicalAge() < 18 && biomedicalView.getBiomedicalGender().equals(GenderByDNA.XY);
                        }
                        case BIOMEDICAL_CHILD -> {
                            return biomedicalView.getBiomedicalAge() < 18;
                        }
                        case BIOMEDICAL_FEMALE -> {
                            return biomedicalView.getBiomedicalGender().equals(GenderByDNA.XX);
                        }
                        case BIOMEDICAL_GIRL -> {
                            return biomedicalView.getBiomedicalAge() < 18 && biomedicalView.getBiomedicalGender().equals(GenderByDNA.XX);
                        }
                        case BIOMEDICAL_MALE -> {
                            return biomedicalView.getBiomedicalGender().equals(GenderByDNA.XY);
                        }
                        case BIOMEDICAL_MAN -> {
                            return biomedicalView.getBiomedicalAge() >= 18 && biomedicalView.getBiomedicalGender().equals(GenderByDNA.XY);
                        }
                        case PERSON -> {
                            return true;
                        }
                        case BIOMEDICAL_WOMAN -> {
                            return biomedicalView.getBiomedicalAge() >= 18 && biomedicalView.getBiomedicalGender().equals(GenderByDNA.XX);
                        }
                    }
                }
                default -> {
                    return false;
                }
            }

        }
        return false;
    }

    @DgsQuery
    public List<DerivedConcept> concepts(@InputArgument String personId) {
        Person person = persons.get(personId);
        if (person == null) {
            return null;
        }
        return findConcepts(person);
    }

    private List<DerivedConcept> findConcepts(Person person) {
        List<DerivedConcept> concepts = new ArrayList<>();
        for (DerivedConcept concept : DerivedConcept.values()) {
            if (checkConcept(person, concept)) {
                concepts.add(concept);
            }
        }
        return concepts;
    }

    @DgsMutation
    public PersonMutationResponse createPerson(@InputArgument String personId) {
        Person newPerson = new Person(personId, new ArrayList<View>());
        persons.put(personId, newPerson);
        return new PersonMutationResponse(200, true, "message", newPerson);
    }

    @DgsMutation
    public PersonMutationResponse addLegalView(@InputArgument String personId, @InputArgument LegalViewInput view) {
        Person person = persons.get(personId);
        person.setViews(person.getViews().stream().filter(v -> !v.getName().equals("Legal View")).collect(Collectors.toList()));
        person.getViews().add(new LegalView("Legal View", view.getLegalAge(), view.getLegalGender()));
        return new PersonMutationResponse(200, true, "message", person);
    }

    @DgsMutation
    public PersonMutationResponse addBiomedicalView(@InputArgument String personId, @InputArgument BiomedicalViewInput view) {
        Person person = persons.get(personId);
        person.setViews(person.getViews().stream().filter(v -> !v.getName().equals("Biomedical View")).collect(Collectors.toList()));
        person.getViews().add(new BiomedicalView("Biomedical View", view.getBiomedicalAge(), view.getBiomedicalGender()));
        return new PersonMutationResponse(200, true, "message", person);
    }

}
