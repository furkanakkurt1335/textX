from __future__ import unicode_literals
from textx import metamodel_from_file, get_children_of_type
import textx.scoping.providers as scoping_providers
import textx.scoping as scoping
from os.path import dirname, abspath, join
from textx.scoping.tools import get_unique_named_object_in_all_models
from pytest import raises


def test_metamodel_provider_advanced_test():
    #################################
    # META MODEL DEF
    #################################
    this_folder = dirname(abspath(__file__))

    def get_meta_model(global_repo, grammar_file_name):
        mm = metamodel_from_file(join(this_folder, grammar_file_name),
                                 debug=False)
        mm.register_scope_providers({
            "*.*": global_repo,
            "Ingredient.unit": scoping_providers.ExtRelativeName("type",
                                                                 "units",
                                                                 "extends")
        })
        return mm

    global_repo = scoping_providers.PlainNameGlobalRepo()
    global_repo.register_models(
        this_folder + "/metamodel_provider2/*.recipe")
    global_repo.register_models(
        this_folder + "/metamodel_provider2/*.ingredient")

    i_mm = get_meta_model(
        global_repo, this_folder + "/metamodel_provider2/Ingredient.tx")
    r_mm = get_meta_model(
        global_repo, this_folder + "/metamodel_provider2/Recipe.tx")

    scoping.MetaModelProvider.add_metamodel("*.recipe", r_mm)
    scoping.MetaModelProvider.add_metamodel("*.ingredient", i_mm)

    #################################
    # MODEL PARSING
    #################################

    model_repo = global_repo.load_models_in_model_repo().all_models

    #################################
    # TEST MODEL
    #################################

    def get_all(model_repo, what):
        lst = []
        for m in model_repo.filename_to_model.values():
            lst = lst + get_children_of_type(what, m)
        return lst

    lst_i = get_all(model_repo, "IngredientType")
    lst_r = get_all(model_repo, "Recipe")

    assert len(lst_i) == 2
    assert len(lst_r) == 2

    # check some references to be resolved (!=None)
    assert lst_r[0].ingredients[0].type
    assert lst_r[0].ingredients[0].unit

    #################################
    # END
    #################################
