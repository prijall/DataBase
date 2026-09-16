import unittest
import processbench_resources as resources


class ResourceTests(unittest.TestCase):
    def test_existing_swap_allowed_but_new_pressure_stops(self):
        base = {'pressure_level':1, 'free_percent':55, 'swap_used_bytes':3*1024**3, 'swapouts_bytes':10*1024**3}
        self.assertEqual(resources.violations(base, base), [])
        for field, value in [('pressure_level',2), ('free_percent',19),
                             ('swap_used_bytes',base['swap_used_bytes']+257*1024**2),
                             ('swapouts_bytes',base['swapouts_bytes']+129*1024**2)]:
            with self.subTest(field=field):
                self.assertTrue(resources.violations(dict(base, **{field:value}), base))

    def test_realistic_telemetry_and_missing_fields(self):
        ctl='kern.memorystatus_vm_pressure_level: 1\nvm.swapusage: total = 4096.00M used = 2844.56M free = 1251.44M'
        pressure='System-wide memory free percentage: 55%'
        vm='Mach Virtual Memory Statistics: (page size of 16384 bytes)\nSwapouts: 469985.'
        result=resources.parse_snapshot(ctl, pressure, vm)
        self.assertEqual(result['swapouts_bytes'], 469985*16384)
        self.assertEqual(result['free_percent'],55)
        with self.assertRaises(ValueError): resources.parse_snapshot(ctl, '', vm)


if __name__ == '__main__': unittest.main()
