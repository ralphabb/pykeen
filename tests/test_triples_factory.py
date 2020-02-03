# -*- coding: utf-8 -*-

"""Test utils for processing numeric literals."""

import unittest

import numpy as np

from pykeen.triples import TriplesFactory, TriplesNumericLiteralsFactory

triples = np.array(
    [
        ['peter', 'likes', 'chocolate_cake'],
        ['chocolate_cake', 'isA', 'dish'],
        ['susan', 'likes', 'pizza'],
        ['peter', 'likes', 'susan'],
    ],
    dtype=np.str,
)

instance_mapped_triples = np.array(
    [
        [0, 0],
        [2, 1],
        [4, 1],
    ],
)

instance_labels = np.array(
    [
        np.array([1]),
        np.array([0, 4]),
        np.array([3]),
    ],
)

numeric_triples = np.array(
    [
        ['peter', '/lit/hasAge', '30'],
        ['peter', '/lit/hasHeight', '185'],
        ['peter', '/lit/hasChildren', '2'],
        ['susan', '/lit/hasAge', '28'],
        ['susan', '/lit/hasHeight', '170'],
    ],
    dtype=np.str,
)


class NumericLiteralsUtilsTests(unittest.TestCase):
    """Class for testing utils for processing numeric literals.tsv."""

    def test_create_lcwa_instances(self):
        """Test creating LCWA instances."""
        factory = TriplesNumericLiteralsFactory(triples=triples, numeric_triples=numeric_triples)
        instances = factory.create_lcwa_instances()

        id_peter = factory.entity_to_id['peter']
        id_age = instances.literals_to_id['/lit/hasAge']
        id_height = instances.literals_to_id['/lit/hasHeight']
        id_num_children = instances.literals_to_id['/lit/hasChildren']

        self.assertEqual(instances.numeric_literals[id_peter, id_age], 30)
        self.assertEqual(instances.numeric_literals[id_peter, id_height], 185)
        self.assertEqual(instances.numeric_literals[id_peter, id_num_children], 2)

        id_susan = factory.entity_to_id['susan']
        id_age = instances.literals_to_id['/lit/hasAge']
        id_height = instances.literals_to_id['/lit/hasHeight']
        id_num_children = instances.literals_to_id['/lit/hasChildren']

        self.assertEqual(instances.numeric_literals[id_susan, id_age], 28)
        self.assertEqual(instances.numeric_literals[id_susan, id_height], 170)
        self.assertEqual(instances.numeric_literals[id_susan, id_num_children], 0)

        id_chocolate_cake = factory.entity_to_id['chocolate_cake']
        id_age = instances.literals_to_id['/lit/hasAge']
        id_height = instances.literals_to_id['/lit/hasHeight']
        id_num_children = instances.literals_to_id['/lit/hasChildren']

        self.assertEqual(instances.numeric_literals[id_chocolate_cake, id_age], 0)
        self.assertEqual(instances.numeric_literals[id_chocolate_cake, id_height], 0)
        self.assertEqual(instances.numeric_literals[id_chocolate_cake, id_num_children], 0)

        # Check if multilabels are working correctly
        self.assertTrue((instance_mapped_triples == instances.mapped_triples.cpu().detach().numpy()).all())
        self.assertTrue(all(all(instance_labels[i] == instances.labels[i]) for i in range(len(instance_labels))))

    def test_triples(self):
        """Test properties of the triples factory."""
        triples_factory = TriplesFactory(triples=triples)
        self.assertEqual(set(range(triples_factory.num_entities)), set(triples_factory.entity_to_id.values()))
        self.assertEqual(set(range(triples_factory.num_relations)), set(triples_factory.relation_to_id.values()))
        self.assertTrue((triples_factory.mapped_triples == triples_factory.map_triples_to_id(triples)).all())

    def test_inverse_triples(self):
        """Test that the right number of entities and triples exist after inverting them."""
        triples_factory = TriplesFactory(triples=triples, create_inverse_triples=True)
        self.assertEqual(set(range(triples_factory.num_entities)), set(triples_factory.entity_to_id.values()))
        self.assertEqual(set(range(triples_factory.num_relations)), set(triples_factory.relation_to_id.values()))

        relations = set(triples[:, 1])
        entities = set(triples[:, 0]).union(triples[:, 2])
        self.assertEqual(len(entities), triples_factory.num_entities)
        self.assertEqual(2, len(relations), msg='Wrong number of relations in set')
        self.assertEqual(2 * len(relations), triples_factory.num_relations, msg='Wrong number of relations in factory')

        self.assertIn('likes_inverse', triples_factory.relation_to_id)
        self.assertEqual(
            triples_factory.relation_to_id['likes'] + triples_factory.num_relations / 2,
            triples_factory.relation_to_id['likes_inverse'],
        )
        self.assertEqual(
            triples_factory.relation_to_id['likes'] + triples_factory.num_relations / 2,
            triples_factory.get_inverse_relation_id('likes'),
        )
