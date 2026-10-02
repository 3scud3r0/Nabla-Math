import unittest

from nablamath.compiler import LogicalDevice, lower_expr, plan_execution
from nablamath.expression import parse_expr


class DistributedPlannerTests(unittest.TestCase):
    def test_plan_is_deterministic_complete_and_valid(self):
        program=lower_expr(parse_expr("((a+b)*(c+d))/((e+f)*(g+h))"))
        devices=(LogicalDevice("gpu0",2.0),LogicalDevice("gpu1",1.0))
        first=plan_execution(program,devices,max_shards_per_device=2)
        second=plan_execution(program,devices,max_shards_per_device=2)
        self.assertEqual(first.to_data(),second.to_data())
        self.assertEqual(first.content_id,second.content_id)
        first.validate(program)
        covered=sorted(i for shard in first.shards for i in shard.instruction_ids)
        self.assertEqual(covered,list(range(len(program.instructions))))
        self.assertEqual(first.shards[first.output_shard].instruction_ids[-1],program.output)

    def test_cross_shard_dependencies_are_explicit(self):
        program=lower_expr(parse_expr("(x+y)*(x+y)+z"))
        plan=plan_execution(program,("cpu0","cpu1"),max_shards_per_device=2)
        owner={i:shard.id for shard in plan.shards for i in shard.instruction_ids}
        for shard in plan.shards:
            needed=set()
            for instruction_id in shard.instruction_ids:
                for arg in program.instructions[instruction_id].args:
                    if owner[arg]!=shard.id:
                        needed.add(owner[arg])
            self.assertTrue(needed <= set(shard.dependencies))

    def test_capacity_biases_load_without_changing_semantics(self):
        program=lower_expr(parse_expr("a+b+c+d+e+f+g+h"))
        plan=plan_execution(
            program,
            (LogicalDevice("big",4.0),LogicalDevice("small",1.0)),
            max_shards_per_device=3,
        )
        plan.validate(program)
        costs={"big":0.0,"small":0.0}
        for shard in plan.shards:
            costs[shard.device]+=shard.estimated_cost
        self.assertGreaterEqual(costs["big"],costs["small"])

    def test_rejects_invalid_device_contract(self):
        program=lower_expr(parse_expr("x+1"))
        with self.assertRaises(ValueError):
            plan_execution(program,())
        with self.assertRaises(ValueError):
            plan_execution(program,(LogicalDevice("x"),LogicalDevice("x")))


if __name__=="__main__":
    unittest.main()
